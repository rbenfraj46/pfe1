from django.db import transaction
from datetime import datetime
from cars.models import AgencyCar, CarUnavailability, Brand, CarModel, GearType
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.generic import CreateView, ListView
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext as _
from cars.models import CarModelRequest
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.http import JsonResponse
from django.core.serializers import serialize
import json
import logging
from django.db.models import Q, Min, Max
from home.models import Agences
from django.contrib.gis.db.models.functions import Distance
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

logger = logging.getLogger(__name__)

@transaction.atomic
def update_car(request, car_id):
    car = get_object_or_404(AgencyCar, id=car_id)
    
    if request.method == 'GET':
        context = {
            'car': car,
            'brands': Brand.objects.filter(is_active=True),
            'car_models': CarModel.objects.filter(is_active=True),
            'gear_types': GearType.objects.filter(is_active=True)
        }
        return render(request, 'car/update_car_form.html', context)
        
    elif request.method == 'POST':
        try:
            car.brand_id = request.POST.get('brand')
            car.car_model_id = request.POST.get('car_model')
            car.gear_type_id = request.POST.get('gear_type')
            car.security_deposit = request.POST.get('security_deposit')
            car.price_per_day = request.POST.get('price_per_day')
            car.fuel_policy = request.POST.get('fuel_policy')
            car.minimum_license_age = request.POST.get('minimum_license_age')
            car.available = request.POST.get('available') == 'on'
            
            if request.FILES.get('image'):
                car.image = request.FILES['image']
                
            car.save()
            
            unavailability_periods_start = request.POST.getlist('unavailability_periods[start][]')
            unavailability_periods_end = request.POST.getlist('unavailability_periods[end][]')

            car.unavailability_periods.all().delete()

            for start, end in zip(unavailability_periods_start, unavailability_periods_end):
                if start and end:
                    start_date = datetime.strptime(start, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end, '%Y-%m-%d').date()
                    CarUnavailability.objects.create(
                        car=car,
                        start_date=start_date,
                        end_date=end_date
                    )
            
            messages.success(request, 'Car updated successfully')
            return redirect('agency_cars')
            
        except Exception as e:
            messages.error(request, f'Error updating car: {str(e)}')
            context = {
                'car': car,
                'brands': Brand.objects.filter(is_active=True),
                'car_models': CarModel.objects.filter(is_active=True),
                'gear_types': GearType.objects.filter(is_active=True)
            }
            return render(request, 'car/update_car_form.html', context)
            
    return redirect('agency_cars')

class CarModelRequestView(View):
    template_name = 'car/request_car_model.html'
    
    def get(self, request, *args, **kwargs):
        context = {
            'brands': Brand.objects.filter(is_active=True)
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        brand_name = request.POST.get('brand_name')
        model_name = request.POST.get('name')
        description = request.POST.get('description')
        
        CarModelRequest.objects.create(
            brand_name=brand_name,
            model_name=model_name,
            description=description,
            status='pending',
            requested_by=request.user
        )
        
        messages.success(request, _('Car model request submitted successfully. Awaiting admin approval.'))
        return redirect('agency_cars_list', agency_id=request.GET.get('agency_id'))

class CarModelRequestHistoryView(LoginRequiredMixin, ListView):
    template_name = 'car/request_car_model_history.html'
    context_object_name = 'requests'
    paginate_by = 10

    def get_queryset(self):
        return CarModelRequest.objects.filter(
            requested_by=self.request.user
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['agency_id'] = self.request.GET.get('agency_id')
        return context

class CarSearchView(View):
    template_name = 'car/search.html'
    
    def get(self, request):
        return render(request, self.template_name)

class CarSearchResultsView(View):
    template_name = 'car/search_results.html'
    
    def get(self, request):
        search_params = {
            'start_date': request.GET.get('start_date'),
            'end_date': request.GET.get('end_date'),
            'latitude': request.GET.get('latitude'),
            'longitude': request.GET.get('longitude'),
            'radius': request.GET.get('radius', 10)
        }
        
        if not all(search_params.values()):
            messages.error(request, _('Missing search parameters'))
            return redirect('car_search')

        point = Point(
            float(search_params['longitude']), 
            float(search_params['latitude']), 
            srid=4326
        )

        cars = self.get_available_cars(point, search_params)
        
        brands = Brand.objects.filter(is_active=True)
        gear_types = GearType.objects.filter(is_active=True)
        price_range = cars.aggregate(min_price=Min('price_per_day'), max_price=Max('price_per_day'))

        price_range = AgencyCar.objects.filter(is_active=True).aggregate(
            min_price=Min('price_per_day'),
            max_price=Max('price_per_day')
        )

        page = request.GET.get('page', 1)
        paginator = Paginator(cars, 6) 
        try:
            cars_page = paginator.page(page)
        except PageNotAnInteger:
            cars_page = paginator.page(1)
        except EmptyPage:
            cars_page = paginator.page(paginator.num_pages)

        context = {
            'cars': cars_page,
            'search_params': search_params,
            'brands': brands,
            'gear_types': gear_types,
            'price_range': price_range,
            'comparison_enabled': True,
            'filters': {
                'min_price': request.GET.get('min_price', price_range['min_price']),
                'max_price': request.GET.get('max_price', price_range['max_price'])
            },
            'sort': request.GET.get('sort', 'distance')
        }
        return render(request, self.template_name, context)

    def get_available_cars(self, point, search_params):
        return AgencyCar.objects.filter(
            agence__location__distance_lte=(point, D(km=float(search_params['radius']))),
            agence__is_active=True,
            is_active=True,
            available=True
        ).exclude(
            unavailability_periods__start_date__lte=search_params['end_date'],
            unavailability_periods__end_date__gte=search_params['start_date']
        ).select_related('brand', 'car_model', 'gear_type', 'agence').annotate(
            distance=Distance('agence__location', point)
        )

class CarSearchFilterView(View):
    def get(self, request):
        search_params = {
            'start_date': request.GET.get('start_date'),
            'end_date': request.GET.get('end_date'),
            'latitude': request.GET.get('latitude'),
            'longitude': request.GET.get('longitude'),
            'radius': request.GET.get('radius', 10)
        }

        point = Point(
            float(search_params['longitude']), 
            float(search_params['latitude']), 
            srid=4326
        )

        cars = self.get_filtered_cars(point, search_params, request.GET)
        
        sort = request.GET.get('sort', 'distance')
        cars = self.apply_sorting(cars, sort)

        page = request.GET.get('page', 1)
        paginator = Paginator(cars, 6) 
        try:
            cars_page = paginator.page(page)
        except PageNotAnInteger:
            cars_page = paginator.page(1)
        except EmptyPage:
            cars_page = paginator.page(paginator.num_pages)

        context = {
            'cars': cars_page,
            'search_params': search_params,
            'filters': {
                'brand': request.GET.get('brand'),
                'gear_types': request.GET.getlist('gear_types'),
                'min_price': request.GET.get('min_price'),
                'max_price': request.GET.get('max_price')
            },
            'sort': sort,
            'comparison_enabled': True
        }
        return render(request, 'car/search_results.html', context)

    def get_filtered_cars(self, point, search_params, filters):
        cars = AgencyCar.objects.filter(
            agence__location__distance_lte=(point, D(km=float(search_params['radius']))),
            agence__is_active=True, 
            is_active=True,
            available=True
        )

        if filters.get('brand'):
            cars = cars.filter(brand_id=filters['brand'])
        
        if filters.getlist('gear_types'):
            cars = cars.filter(gear_type_id__in=filters.getlist('gear_types'))
        
        if filters.get('price'):
            cars = cars.filter(price_per_day__lte=filters['price'])

        return cars.select_related('brand', 'car_model', 'gear_type', 'agence').annotate(
            distance=Distance('agence__location', point)
        )

    def apply_sorting(self, queryset, sort):
        if sort == 'price_asc':
            return queryset.order_by('price_per_day')
        elif sort == 'price_desc':
            return queryset.order_by('-price_per_day')
        else: 
            return queryset.order_by('distance')

class CarRentalRequestView(LoginRequiredMixin, View):
    template_name = 'car/rental_request.html'

    def get(self, request, car_id):
        car = get_object_or_404(AgencyCar, id=car_id)
        context = {
            'car': car,
            'start_date': request.GET.get('start_date'),
            'end_date': request.GET.get('end_date')
        }
        return render(request, self.template_name, context)

    def post(self, request, car_id):
        car = get_object_or_404(AgencyCar, id=car_id)
        messages.success(request, _('Rental request submitted successfully'))
        return redirect('car_search_results')