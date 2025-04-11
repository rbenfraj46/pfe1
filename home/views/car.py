from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import logging
from datetime import datetime

from cars.models import (
    AgencyCar, 
    CarUnavailability, 
    Brand, 
    CarModel, 
    GearType,
    CarModelRequest,
    CarReservation
)
from home.models import Agences
from home.views.agences import has_agency_permission

logger = logging.getLogger(__name__)

class CarManagementMixin:
    """Mixin pour la gestion commune des voitures"""
    def get_car_form_context(self, agency=None, car=None):
        context = {
            'brands': Brand.objects.filter(is_active=True),
            'gear_types': GearType.objects.filter(is_active=True),
        }
        
        if car and car.brand:
            context['car_models'] = CarModel.objects.filter(brand=car.brand)
        else:
            context['car_models'] = []
            
        if agency:
            context['selected_agency'] = agency
        if car:
            context['car'] = car
            
        return context

class CarRentalRequestView(LoginRequiredMixin, View):
    template_name = 'car/rental_request.html'
    login_url = '/login.php'  # URL de connexion correcte

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
        try:
            # Conversion des dates depuis les chaînes de caractères
            start_date = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d').date()
            
            # Calcul du nombre de jours et du prix total
            days = (end_date - start_date).days
            total_price = car.price_per_day * days
            
            reservation = CarReservation.objects.create(
                car=car,
                user=request.user,
                start_date=start_date,
                end_date=end_date,
                notes=request.POST.get('notes'),
                status='pending',
                total_price=total_price
            )
            
            # Envoyer une notification à l'agence
            subject = _('New Rental Request')
            message = _('''A new rental request has been submitted for your car:
                Car: {car}
                Customer: {user}
                From: {start}
                To: {end}
                Total Price: {price}
                Notes: {notes}
                
                Please review this request in your admin panel.
            ''').format(
                car=car,
                user=request.user.get_full_name() or request.user.username,
                start=reservation.start_date,
                end=reservation.end_date,
                price=reservation.total_price,
                notes=reservation.notes or _('No special notes')
            )
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [car.agence.email],
                    fail_silently=True
                )
            except Exception as e:
                logger.error(f"Failed to send email to agency: {str(e)}")

            messages.success(
                request, 
                _('Your rental request has been submitted successfully. Please wait for the agency approval.')
            )
            return redirect('index')
            
        except (ValueError, TypeError) as e:
            messages.error(request, _('Invalid date format. Please use YYYY-MM-DD format.'))
            context = {
                'car': car,
                'start_date': request.POST.get('start_date'),
                'end_date': request.POST.get('end_date'),
                'notes': request.POST.get('notes')
            }
            return render(request, self.template_name, context)
        except ValidationError as e:
            messages.error(request, str(e))
            context = {
                'car': car,
                'start_date': request.POST.get('start_date'),
                'end_date': request.POST.get('end_date'),
                'notes': request.POST.get('notes')
            }
            return render(request, self.template_name, context)
        except Exception as e:
            messages.error(request, _('An error occurred while processing your request.'))
            logger.error(f"Error creating reservation: {str(e)}")
            return redirect('car_search_results')

class CarModelRequestView(LoginRequiredMixin, View):
    template_name = 'car/request_car_model.html'
    
    def get(self, request, *args, **kwargs):
        context = {
            'brands': Brand.objects.filter(is_active=True)
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        CarModelRequest.objects.create(
            brand_name=request.POST.get('brand_name'),
            model_name=request.POST.get('name'),
            description=request.POST.get('description'),
            status='pending',
            requested_by=request.user
        )
        
        messages.success(request, _('Car model request submitted successfully. Awaiting admin approval.'))
        return redirect('agency_cars_list', agency_id=request.GET.get('agency_id'))

class CarModelRequestHistoryView(LoginRequiredMixin, View):
    template_name = 'car/request_car_model_history.html'
    paginate_by = 10

    def get(self, request):
        requests = CarModelRequest.objects.filter(
            requested_by=request.user
        ).order_by('-created_at')
        
        paginator = Paginator(requests, self.paginate_by)
        page = request.GET.get('page', 1)
        
        try:
            requests_page = paginator.page(page)
        except PageNotAnInteger:
            requests_page = paginator.page(1)
        except EmptyPage:
            requests_page = paginator.page(paginator.num_pages)

        context = {
            'requests': requests_page,
            'agency_id': request.GET.get('agency_id')
        }
        return render(request, self.template_name, context)

class UpdateCarView(LoginRequiredMixin, CarManagementMixin, View):
    template_name = "car/update_car_form.html"

    def dispatch(self, request, *args, **kwargs):
        car = get_object_or_404(AgencyCar, pk=kwargs.get('pk'))
        agency_id = car.agence.id
        
        if not (car.agence.creator == request.user or 
                has_agency_permission(request.user, agency_id, 'edit')):
            raise PermissionDenied
            
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        car = get_object_or_404(AgencyCar, pk=kwargs.get('pk'))
        context = self.get_car_form_context(car=car)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        car = get_object_or_404(AgencyCar, pk=kwargs.get('pk'))
        
        try:
            car.brand_id = request.POST.get('brand')
            car.car_model_id = request.POST.get('car_model')
            car.fuel_policy = request.POST.get('fuel_policy')
            car.security_deposit = request.POST.get('security_deposit')
            car.minimum_license_age = request.POST.get('minimum_license_age')
            car.price_per_day = request.POST.get('price_per_day')
            car.available = request.POST.get('available') == 'on'
            car.gear_type_id = request.POST.get('gear_type')
            
            if request.FILES.get('image'):
                car.image = request.FILES.get('image')
                
            car.save()
            
            # Mise à jour des périodes d'indisponibilité
            car.unavailability_periods.all().delete()
            start_dates = request.POST.getlist('unavailability_periods[start][]')
            end_dates = request.POST.getlist('unavailability_periods[end][]')
            
            for start_date, end_date in zip(start_dates, end_dates):
                if start_date and end_date:
                    CarUnavailability.objects.create(
                        car=car,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
            messages.success(request, _('Car updated successfully'))
            return redirect('agency_cars_list', agency_id=car.agence.id)
            
        except Exception as e:
            messages.error(request, f'Error updating car: {str(e)}')
            context = self.get_car_form_context(car=car)
            return render(request, self.template_name, context)

class DeleteCarView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        car = get_object_or_404(AgencyCar, pk=kwargs.get('pk'))
        agency_id = car.agence.id
        
        if not (car.agence.creator == request.user or 
                has_agency_permission(request.user, agency_id, 'delete')):
            raise PermissionDenied
            
        try:
            car.is_active = False
            car.save()
            messages.success(request, _('Car deleted successfully'))
            return JsonResponse({'success': True})
        except Exception as e:
            messages.error(request, f'Error deleting car: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)})

class AgencyCarsListView(LoginRequiredMixin, ListView):
    template_name = 'car/agency_cars_list.html'
    context_object_name = 'agency_cars'
    paginate_by = 10

    def get_queryset(self):
        agency_id = self.kwargs.get('agency_id')
        agency = get_object_or_404(Agences, id=agency_id)
        
        if agency.creator == self.request.user:
            return AgencyCar.objects.filter(agence_id=agency_id, is_active=True)
        
        if has_agency_permission(self.request.user, agency_id, 'view'):
            return AgencyCar.objects.filter(agence_id=agency_id, is_active=True)
        
        raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agency_id = self.kwargs.get('agency_id')
        agency = get_object_or_404(Agences, id=agency_id)
        
        context.update({
            'can_add': (agency.creator == self.request.user or 
                       has_agency_permission(self.request.user, agency_id, 'add')),
            'can_edit': (agency.creator == self.request.user or 
                        has_agency_permission(self.request.user, agency_id, 'edit')),
            'can_delete': (agency.creator == self.request.user or 
                          has_agency_permission(self.request.user, agency_id, 'delete')),
            'selected_agency': agency,
            'brands': Brand.objects.filter(is_active=True),
            'gear_types': GearType.objects.filter(is_active=True)
        })
        return context

class RegisterCarView(LoginRequiredMixin, CarManagementMixin, View):
    template_name = "car/car_form.html"

    def dispatch(self, request, *args, **kwargs):
        agency_id = kwargs.get('agency_id')
        agency = get_object_or_404(Agences, id=agency_id)
        
        if not (agency.creator == request.user or 
                has_agency_permission(request.user, agency_id, 'add')):
            raise PermissionDenied
            
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        agency_id = kwargs.get('agency_id')
        agency = get_object_or_404(Agences, id=agency_id, creator=request.user, is_active=True)
        context = self.get_car_form_context(agency=agency)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        agency_id = kwargs.get('agency_id')
        agency = get_object_or_404(Agences, id=agency_id, creator=request.user, is_active=True)

        try:
            car = AgencyCar(
                agence=agency,
                brand_id=request.POST.get('brand'),
                car_model_id=request.POST.get('car_model'),
                fuel_policy=request.POST.get('fuel_policy'),
                security_deposit=request.POST.get('security_deposit'),
                minimum_license_age=request.POST.get('minimum_license_age'),
                price_per_day=request.POST.get('price_per_day'),
                is_active=agency.is_auto,
                available=request.POST.get('available') == 'on',
                gear_type_id=request.POST.get('gear_type')
            )
            
            if request.FILES.get('image'):
                car.image = request.FILES['image']
                
            car.save()
            
            # Gestion des périodes d'indisponibilité
            start_dates = request.POST.getlist('unavailability_periods[start][]')
            end_dates = request.POST.getlist('unavailability_periods[end][]')
            
            for start_date, end_date in zip(start_dates, end_dates):
                if start_date and end_date:
                    CarUnavailability.objects.create(
                        car=car,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
            messages.success(request, _('Car added successfully'))
            return redirect('agency_cars_list', agency_id=agency_id)
            
        except Exception as e:
            messages.error(request, f'Error adding car: {str(e)}')
            context = self.get_car_form_context(agency=agency)
            return render(request, self.template_name, context)

class CarModelsJsonView(View):
    """Vue pour récupérer les modèles de voiture en format JSON pour un usage AJAX"""
    def get(self, request, *args, **kwargs):
        brand_id = request.GET.get('brand_id')
        models = CarModel.objects.filter(
            brand_id=brand_id, 
            is_active=True
        ).values('id', 'name')
        return JsonResponse(list(models), safe=False)

class CarModelDetailsView(DetailView):
    """Vue pour afficher les détails d'un modèle de voiture"""
    model = CarModel
    template_name = 'car/model_details.html'
    context_object_name = 'car_model'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        car_model = self.get_object()
        context.update({
            'brand': car_model.brand,
            'available_cars': AgencyCar.objects.filter(
                car_model=car_model,
                is_active=True,
                available=True
            ).select_related('agence')
        })
        return context