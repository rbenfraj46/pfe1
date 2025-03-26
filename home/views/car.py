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