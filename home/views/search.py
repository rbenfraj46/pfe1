from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Min, Max
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.utils.translation import gettext as _
import logging

from cars.models import AgencyCar, Brand, GearType

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
        return Point(float(longitude), float(latitude), srid=4326)

    def get_available_cars(self, point, search_params, filters=None):
        logger.info(f"Recherche de voitures avec les paramètres: {search_params}")
        
        # Base query pour les voitures actives et disponibles
        cars = AgencyCar.objects.select_related(
            'brand', 'car_model', 'gear_type', 'agence'
        ).filter(
            is_active=True,
            available=True
        )

        # Filtre par distance
        cars = cars.filter(
            agence__location__distance_lte=(point, D(km=float(search_params['radius'])))
        )

        # Exclure les voitures indisponibles pour les dates sélectionnées
        if search_params.get('start_date') and search_params.get('end_date'):
            cars = cars.exclude(
                unavailability_periods__start_date__lte=search_params['end_date'],
                unavailability_periods__end_date__gte=search_params['start_date']
            )

        # Appliquer les filtres supplémentaires
        if filters:
            if filters.get('brand'):
                cars = cars.filter(brand_id=filters['brand'])
            
            if filters.get('gear_types'):
                cars = cars.filter(gear_type_id__in=filters['gear_types'])
            
            if filters.get('min_price') and filters.get('max_price'):
                cars = cars.filter(
                    price_per_day__gte=filters.get('min_price'),
                    price_per_day__lte=filters.get('max_price')
                )

        # Ajouter la distance
        cars = cars.annotate(
            distance=Distance('agence__location', point)
        )

        logger.info(f"Nombre de voitures trouvées: {cars.count()}")
        return cars

    def apply_filters(self, queryset, filters):
        if filters.get('brand'):
            queryset = queryset.filter(brand_id=filters['brand'])
        
        if filters.get('gear_types'):
            queryset = queryset.filter(gear_type_id__in=filters['gear_types'])
        
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
            max_price=Max('price_per_day')
        )

    def get_current_filters(self):
        price_range = self.get_price_range()
        return {
            'min_price': self.request.GET.get('min_price', price_range['min_price']),
            'max_price': self.request.GET.get('max_price', price_range['max_price']),
            'brand': self.request.GET.get('brand', ''),
            'gear_types': self.request.GET.getlist('gear_types', [])
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
            'min_price': request.GET.get('min_price'),
            'max_price': request.GET.get('max_price')
        }

        cars = self.get_available_cars(point, search_params, filter_params)
        sort = request.GET.get('sort', 'distance')
        cars = self.apply_sorting(cars, sort)

        context = self.get_context_data(
            cars=self.paginate_cars(cars, request),
            search_params=search_params,
            sort=sort,
            filters=filter_params  # Ajouter les filtres au contexte
        )
        return render(request, self.template_name, context)