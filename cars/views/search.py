from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Min, Max, Q
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.utils.translation import gettext as _
import logging
from django.http import JsonResponse

from cars.models import AgencyCar, Brand, GearType
from home.models import Agences

logger = logging.getLogger(__name__)

class CarSearchMixin:
    """Mixin pour la fonctionnalité de recherche de voiture commune"""
    def get_search_params(self, request):
        return {
            'start_date': request.GET.get('start_date'),
            'end_date': request.GET.get('end_date'),
            'latitude': request.GET.get('latitude'),
            'longitude': request.GET.get('longitude'),
            'radius': request.GET.get('radius', 10)
        }

    def get_point_from_coords(self, latitude, longitude):
        try:
            if latitude and longitude:
                return Point(float(longitude), float(latitude), srid=4326)
            return None
        except (ValueError, TypeError) as e:
            logger.error(f"Erreur de conversion des coordonnées: {e}")
            return None

    def get_available_cars(self, point, search_params, filters=None):
        base_query = AgencyCar.objects.filter(
            is_active=True,
            available=True,
            agence__is_active=True
        )
        if point:
            radius_km = float(search_params.get('radius', 10))
            base_query = base_query.filter(
                agence__location__dwithin=(point, radius_km / 111.0)
            ).annotate(
                distance=Distance('agence__location', point)
            )
        if search_params.get('start_date') and search_params.get('end_date'):
            unavailable = AgencyCar.objects.filter(
                Q(
                    unavailability_periods__start_date__lte=search_params['end_date'],
                    unavailability_periods__end_date__gte=search_params['start_date']
                ) |
                Q(
                    reservations__status='approved',
                    reservations__start_date__lte=search_params['end_date'],
                    reservations__end_date__gte=search_params['start_date']
                )
            )
            base_query = base_query.exclude(id__in=unavailable.values('id'))
        if filters:
            base_query = self.apply_filters(base_query, filters)
        return base_query.select_related(
            'brand', 'car_model', 'gear_type', 'agence'
        )

    def apply_filters(self, queryset, filters):
        if filters.get('brand'):
            queryset = queryset.filter(brand_id=filters['brand'])
        if filters.get('gear_types'):
            queryset = queryset.filter(gear_type_id__in=filters['gear_types'])
        if filters.get('fuel_types'):
            queryset = queryset.filter(fuel_policy__in=filters['fuel_types'])
        if filters.get('categories'):
            queryset = queryset.filter(car_model__category__in=filters['categories'])
        if filters.get('min_deposit') and filters.get('max_deposit'):
            queryset = queryset.filter(
                security_deposit__gte=filters.get('min_deposit'),
                security_deposit__lte=filters.get('max_deposit')
            )
        if filters.get('with_driver') is not None:
            queryset = queryset.filter(with_driver=filters.get('with_driver'))
            
        min_price = int(filters.get('min_price') or 40)
        max_price = int(filters.get('max_price') or 4000)
        return queryset.filter(price_per_day__gte=min_price, price_per_day__lte=max_price)

    def apply_sorting(self, queryset, sort):
        if sort == 'price_asc':
            return queryset.order_by('price_per_day')
        elif sort == 'price_desc':
            return queryset.order_by('-price_per_day')
        return queryset.order_by('distance')

class CarSearchView(View):
    template_name = 'car/search.html'
    def get(self, request):
        return render(request, self.template_name)

class CarSearchResultsView(CarSearchMixin, View):
    template_name = 'car/search_results.html'
    items_per_page = 6
    def get(self, request):
        search_params = self.get_search_params(request)
        if not all([search_params['start_date'], search_params['end_date'], 
                   search_params['latitude'], search_params['longitude']]):
            messages.error(request, _('Missing search parameters'))
            return redirect('index')
        point = self.get_point_from_coords(
            search_params['latitude'], 
            search_params['longitude']
        )
        cars = self.get_available_cars(point, search_params)
        sort = request.GET.get('sort', 'distance')
        cars = self.apply_sorting(cars, sort)
        context = self.get_context_data(
            cars=self.paginate_cars(cars, request),
            search_params=search_params,
            sort=sort
        )
        return render(request, self.template_name, context)
    def paginate_cars(self, cars, request):
        paginator = Paginator(cars, self.items_per_page)
        page = request.GET.get('page', 1)
        try:
            return paginator.page(page)
        except PageNotAnInteger:
            return paginator.page(1)
        except EmptyPage:
            return paginator.page(paginator.num_pages)
    def get_context_data(self, **kwargs):
        context = kwargs
        context.update({
            'brands': Brand.objects.filter(is_active=True),
            'gear_types': GearType.objects.filter(is_active=True),
            'price_range': self.get_price_range(),
            'comparison_enabled': True,
            'filters': self.get_current_filters()
        })
        return context
    def get_price_range(self):
        return AgencyCar.objects.filter(is_active=True).aggregate(
            min_price=Min('price_per_day'),
            max_price=Max('price_per_day'),
            min_deposit=Min('security_deposit'),
            max_deposit=Max('security_deposit')
        )
    def get_current_filters(self):
        price_range = self.get_price_range()
        return {
            'min_price': self.request.GET.get('min_price', price_range['min_price']),
            'max_price': self.request.GET.get('max_price', price_range['max_price']),
            'min_deposit': self.request.GET.get('min_deposit', price_range['min_deposit']),
            'max_deposit': self.request.GET.get('max_deposit', price_range['max_deposit']),
            'brand': self.request.GET.get('brand', ''),
            'gear_types': self.request.GET.getlist('gear_types', []),
            'fuel_types': self.request.GET.getlist('fuel_types', []),
            'categories': self.request.GET.getlist('categories', [])
        }

class CarSearchFilterView(CarSearchResultsView):
    def get(self, request):
        search_params = self.get_search_params(request)
        if not all([search_params['start_date'], search_params['end_date'], 
                   search_params['latitude'], search_params['longitude']]):
            messages.error(request, _('Missing search parameters'))
            return redirect('index')
        point = self.get_point_from_coords(
            search_params['latitude'], 
            search_params['longitude']
        )
        filter_params = {
            'brand': request.GET.get('brand'),
            'gear_types': request.GET.getlist('gear_types'),
            'fuel_types': request.GET.getlist('fuel_types'),
            'categories': request.GET.getlist('categories'),
            'min_price': request.GET.get('min_price'),
            'max_price': request.GET.get('max_price'),
            'min_deposit': request.GET.get('min_deposit'),
            'max_deposit': request.GET.get('max_deposit')
        }
        cars = self.get_available_cars(point, search_params, filter_params)
        sort = request.GET.get('sort', 'distance')
        cars = self.apply_sorting(cars, sort)
        context = self.get_context_data(
            cars=self.paginate_cars(cars, request),
            search_params=search_params,
            sort=sort,
            filters=filter_params
        )
        return render(request, self.template_name, context)

class CarSearchDebugView(CarSearchMixin, View):
    def get(self, request):
        search_params = self.get_search_params(request)
        point = self.get_point_from_coords(
            search_params['latitude'],
            search_params['longitude']
        )
        base_cars = AgencyCar.objects.filter(
            is_active=True,
            available=True,
            agence__is_active=True
        )
        all_agencies = Agences.objects.filter(is_active=True).values('id', 'agency_name', 'location')
        agencies_info = []
        for agency in all_agencies:
            if agency['location']:
                agencies_info.append({
                    'id': agency['id'],
                    'name': agency['agency_name'],
                    'location': str(agency['location']),
                    'distance_km': None
                })
                if point:
                    distance = Distance('location', point)
                    agency_with_distance = Agences.objects.annotate(
                        distance=distance
                    ).get(id=agency['id'])
                    agencies_info[-1]['distance_km'] = agency_with_distance.distance.km
        cars_in_radius = base_cars.filter(
            agence__location__dwithin=(point, float(search_params['radius']) / 111.0)
        ) if point else base_cars
        unavailable_cars = set()
        if search_params.get('start_date') and search_params.get('end_date'):
            unavailable_cars.update(
                AgencyCar.objects.filter(
                    unavailability_periods__start_date__lte=search_params['end_date'],
                    unavailability_periods__end_date__gte=search_params['start_date']
                ).values_list('id', flat=True)
            )
            unavailable_cars.update(
                AgencyCar.objects.filter(
                    reservations__status='approved',
                    reservations__start_date__lte=search_params['end_date'],
                    reservations__end_date__gte=search_params['start_date']
                ).values_list('id', flat=True)
            )
        filter_params = {
            'brand': request.GET.get('brand'),
            'gear_types': request.GET.getlist('gear_types'),
            'min_price': request.GET.get('min_price', 40),
            'max_price': request.GET.get('max_price', 4000)
        }
        filtered_cars = self.apply_filters(cars_in_radius, filter_params)
        available_cars = filtered_cars.exclude(id__in=unavailable_cars)
        response_data = {
            'debug_info': {
                'search_params': search_params,
                'point': str(point) if point else None,
                'total_active_cars': base_cars.count(),
                'cars_in_radius': cars_in_radius.count(),
                'unavailable_cars': len(unavailable_cars),
                'cars_after_filters': filtered_cars.count(),
                'final_available_cars': available_cars.count(),
                'filters_applied': filter_params,
                'agencies': agencies_info,
                'radius_in_degrees': float(search_params['radius']) / 111.0,
                'cars_in_radius_list': list(cars_in_radius.values(
                    'id', 'brand__name', 'car_model__name', 
                    'agence__agency_name', 'agence__location'
                )),
                'unavailable_cars_list': list(AgencyCar.objects.filter(
                    id__in=unavailable_cars
                ).values(
                    'id', 'brand__name', 'car_model__name', 
                    'agence__agency_name', 'agence__location'
                ))
            }
        }
        return JsonResponse(response_data)