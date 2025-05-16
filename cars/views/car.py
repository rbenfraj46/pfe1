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
from django.utils import timezone
import logging
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from cars.models import (
    AgencyCar, 
    CarUnavailability, 
    Brand, 
    CarModel, 
    GearType,
    CarModelRequest,
    CarReservation,
    CarPromotion
)
from home.models import Agences
from home.views.agences import has_agency_permission
from home.mail_util import send_car_rental_notification

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
    login_url = '/login.php'

    def get(self, request, car_id):
        car = get_object_or_404(AgencyCar, id=car_id)
        
        # Si c'est une requête AJAX pour calculer le total
        if request.GET.get('calculate_total'):
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            total_info = car.calculate_total_price(start_date, end_date)
            
            return JsonResponse({
                'success': True,
                'total': total_info
            } if total_info else {
                'success': False,
                'error': _('Invalid dates')
            })
        
        context = {
            'car': car,
            'start_date': request.GET.get('start_date'),
            'end_date': request.GET.get('end_date'),
            'today': timezone.now().date()
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
            
            # Send notification to agency
            send_car_rental_notification(reservation, 'request', request=request)
            
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
            return redirect('index')

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
            car.minimum_rental_days = request.POST.get('minimum_rental_days')
            car.price_per_day = request.POST.get('price_per_day')
            car.available = request.POST.get('available') == 'on'
            car.gear_type_id = request.POST.get('gear_type')
            
            # Gestion des informations du chauffeur
            car.with_driver = request.POST.get('with_driver') == 'on'
            if car.with_driver:
                car.driver_name = request.POST.get('driver_name')
                car.driver_phone = request.POST.get('driver_phone')
                car.driver_license_number = request.POST.get('driver_license_number')
                car.driver_experience_years = request.POST.get('driver_experience_years')
                car.driver_languages = request.POST.get('driver_languages')
                car.security_deposit = 0  # Pas de caution pour les voitures avec chauffeur
            else:
                car.driver_name = None
                car.driver_phone = None
                car.driver_license_number = None
                car.driver_experience_years = None
                car.driver_languages = None
            
            # Gestion des informations de transfert
            car.for_transfer = request.POST.get('for_transfer') == 'on'
            if car.for_transfer:
                car.price_per_km = request.POST.get('price_per_km')
                car.price_per_hour = request.POST.get('price_per_hour')
                car.max_passengers = request.POST.get('max_passengers')
                car.max_luggage_pieces = request.POST.get('max_luggage_pieces')
                car.max_luggage_weight = request.POST.get('max_luggage_weight')
            else:
                car.price_per_km = None
                car.price_per_hour = None
                car.max_passengers = None
                car.max_luggage_pieces = None
                car.max_luggage_weight = None
            
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
                    
            # Handle promotion
            has_promotion = request.POST.get('has_promotion') == 'on'
            if has_promotion:
                promotion_data = {
                    'percentage': int(request.POST.get('promotion_percentage')),
                    'start_date': request.POST.get('promotion_start_date'),
                    'end_date': request.POST.get('promotion_end_date'),
                }
                
                # Deactivate any existing promotions
                car.promotions.filter(is_active=True).update(is_active=False)
                
                # Create new promotion
                CarPromotion.objects.create(
                    car=car,
                    percentage=promotion_data['percentage'],
                    start_date=promotion_data['start_date'],
                    end_date=promotion_data['end_date'],
                    is_active=True
                )
            else:
                # Deactivate all promotions if checkbox is unchecked
                car.promotions.filter(is_active=True).update(is_active=False)

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

class AgencyCarListView(LoginRequiredMixin, View):
    template_name = 'car/agency_cars_list.html'
    items_per_page = 10

    def get(self, request, agency_id):
        user = request.user
        selected_agency = get_object_or_404(Agences, id=agency_id)
        
        # Vérifier si l'utilisateur est le créateur ou a la permission de voir
        if not (selected_agency.creator == user or has_agency_permission(user, agency_id, 'view')):
            raise PermissionDenied

        # Vérifier les permissions spécifiques
        can_add = selected_agency.creator == user or has_agency_permission(user, agency_id, 'add')
        can_edit = selected_agency.creator == user or has_agency_permission(user, agency_id, 'edit')
        can_delete = selected_agency.creator == user or has_agency_permission(user, agency_id, 'delete')
        
        # Filtrer pour ne montrer que les voitures actives
        queryset = AgencyCar.objects.filter(agence=selected_agency, is_active=True)
        
        # Appliquer les filtres
        brand = request.GET.get('brand')
        gear_type = request.GET.get('gear_type')
        with_driver = request.GET.get('with_driver')

        if brand:
            queryset = queryset.filter(brand__name=brand)
        if gear_type:
            queryset = queryset.filter(gear_type__name=gear_type)
        if with_driver:
            queryset = queryset.filter(with_driver=with_driver == '1')

        # Pagination
        paginator = Paginator(queryset, self.items_per_page)
        page = request.GET.get('page', 1)
        
        try:
            agency_cars = paginator.page(page)
        except PageNotAnInteger:
            agency_cars = paginator.page(1)
        except EmptyPage:
            agency_cars = paginator.page(paginator.num_pages)

        context = {
            'selected_agency': selected_agency,
            'agency_cars': agency_cars,
            'page_obj': agency_cars,
            'paginator': paginator,
            'brands': Brand.objects.all(),
            'gear_types': GearType.objects.all(),
            'can_add': can_add,
            'can_edit': can_edit,
            'can_delete': can_delete
        }
        
        return render(request, self.template_name, context)

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
                minimum_rental_days=request.POST.get('minimum_rental_days'),
                price_per_day=request.POST.get('price_per_day'),
                is_active=agency.is_auto,
                available=request.POST.get('available') == 'on',
                gear_type_id=request.POST.get('gear_type'),
                with_driver=request.POST.get('with_driver') == 'on'
            )
            
            # Gestion des informations du chauffeur si la voiture est avec chauffeur
            if car.with_driver:
                car.driver_name = request.POST.get('driver_name')
                car.driver_phone = request.POST.get('driver_phone')
                car.driver_license_number = request.POST.get('driver_license_number')
                car.driver_experience_years = request.POST.get('driver_experience_years')
                car.driver_languages = request.POST.get('driver_languages')
                car.security_deposit = 0  # Pas de caution pour les voitures avec chauffeur

            # Gestion des informations de transfert
            car.for_transfer = request.POST.get('for_transfer') == 'on'
            if car.for_transfer:
                car.price_per_km = request.POST.get('price_per_km')
                car.price_per_hour = request.POST.get('price_per_hour')
                car.max_passengers = request.POST.get('max_passengers')
                car.max_luggage_pieces = request.POST.get('max_luggage_pieces')
                car.max_luggage_weight = request.POST.get('max_luggage_weight')
            
            if request.FILES.get('image'):
                car.image = request.FILES['image']
            
            car.save()
            
            # Gestion des promotions
            has_promotion = request.POST.get('has_promotion') == 'on'
            if has_promotion:
                promotion_data = {
                    'percentage': int(request.POST.get('promotion_percentage')),
                    'start_date': request.POST.get('promotion_start_date'),
                    'end_date': request.POST.get('promotion_end_date'),
                }
                
                # Création de la promotion
                CarPromotion.objects.create(
                    car=car,
                    percentage=promotion_data['percentage'],
                    start_date=promotion_data['start_date'],
                    end_date=promotion_data['end_date'],
                    is_active=True
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

class UserReservationsView(LoginRequiredMixin, ListView):
    template_name = 'car/user_reservations.html'
    context_object_name = 'reservations'
    paginate_by = 10

    def get_queryset(self):
        return CarReservation.objects.filter(
            user=self.request.user
        ).select_related(
            'car__brand', 
            'car__car_model', 
            'car__agence'
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_count'] = self.get_queryset().filter(status='pending').count()
        context['approved_count'] = self.get_queryset().filter(status='approved').count()
        context['rejected_count'] = self.get_queryset().filter(status='rejected').count()
        context['cancelled_count'] = self.get_queryset().filter(status='cancelled').count()
        return context

class CancelReservationView(LoginRequiredMixin, View):
    def post(self, request, reservation_id):
        try:
            reservation = get_object_or_404(
                CarReservation.objects.select_related('car__agence'), 
                id=reservation_id,
                user=request.user
            )
            
            if reservation.status != 'pending':
                return JsonResponse({
                    'success': False,
                    'message': _('Only pending reservations can be cancelled.')
                }, status=400)
                
            reservation.status = 'cancelled'
            reservation.save()
            
            # Send notification email to agency
            try:
                send_car_rental_notification(reservation, 'cancelled')
            except Exception as e:
                logger.error(f"Failed to send cancellation email: {str(e)}")

            return JsonResponse({
                'success': True,
                'message': _('Reservation cancelled successfully.')
            })
            
        except CarReservation.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': _('Reservation not found.')
            }, status=404)
        except Exception as e:
            logger.error(f"Error cancelling reservation {reservation_id}: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': _('Failed to cancel reservation. Please try again.')
            }, status=500)

class CarDetailView(DetailView):
    """Vue pour afficher les détails détaillés d'une voiture"""
    model = AgencyCar
    template_name = 'car/car_detail.html'
    context_object_name = 'car'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        car = self.get_object()
        context.update({
            'is_available': car.is_available(
                self.request.GET.get('start_date'), 
                self.request.GET.get('end_date')
            ) if self.request.GET.get('start_date') and self.request.GET.get('end_date') else True,
        })
        return context

@method_decorator(csrf_exempt, name='dispatch')
class CalculateRentalTotalView(View):
    def get(self, request):
        try:
            car_id = request.GET.get('car_id')
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')

            if not all([car_id, start_date, end_date]):
                return JsonResponse({
                    'success': False,
                    'message': _('Missing required parameters')
                })

            car = get_object_or_404(AgencyCar, id=car_id)
            price_info = car.calculate_total_price(start_date, end_date)

            if not price_info:
                return JsonResponse({
                    'success': False,
                    'message': _('Invalid date range or minimum rental period not met')
                })

            promotion = car.get_current_promotion()
            response_data = {
                'success': True,
                'days': price_info['days'],
                'price_per_day': price_info['price_per_day'],
                'discounted_price_per_day': price_info['discounted_price_per_day'],
                'security_deposit': price_info['security_deposit'],
                'total_price': price_info['total_price'],
                'minimum_rental_days': price_info['minimum_rental_days'],
                'promotion': price_info['promotion']
            }

            return JsonResponse(response_data)

        except AgencyCar.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': _('Car not found')
            })
        except Exception as e:
            logger.error(f"Error calculating rental total: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': _('An error occurred while calculating the total')
            })