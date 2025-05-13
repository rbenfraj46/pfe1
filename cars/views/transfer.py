from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.gis.geos import Point
from django.db.models import Q
import logging
from datetime import datetime
from decimal import Decimal

from cars.models import AgencyCar, TransferBooking
from home.models import Agences
from home.views.agences import has_agency_permission

logger = logging.getLogger(__name__)


class TransferSearchView(View):
    template_name = 'transfer/search.html'
    
    def get(self, request):
        return render(request, self.template_name)

class TransferSearchResultsView(View):
    template_name = 'transfer/search_results.html'
    items_per_page = 10
    
    def _safe_float(self, value, default=0.0):
        """Convertir une valeur en float de manière sécurisée"""
        try:
            if value and str(value).strip():
                return float(value)
            return default
        except (ValueError, TypeError):
            return default

    def _safe_int(self, value, default=0):
        """Convertir une valeur en int de manière sécurisée"""
        try:
            if value and str(value).strip():
                return int(value)
            return default
        except (ValueError, TypeError):
            return default

    def _calculate_price(self, vehicle, pricing_type, hours=None, distance=None):
        """Calculer le prix total pour un véhicule"""
        try:
            if not vehicle.for_transfer:
                return 0

            if pricing_type == 'hourly' and hours and hasattr(vehicle, 'price_per_hour'):
                # Convertir Decimal en float pour le calcul
                hourly_rate = float(vehicle.price_per_hour)
                total = hourly_rate * float(hours)
                return {
                    'total': total,
                    'details': {
                        'rate_per_hour': hourly_rate,
                        'hours': float(hours),
                        'calculation': f"{hourly_rate} × {hours}"
                    }
                }
            
            elif pricing_type == 'distance' and distance and hasattr(vehicle, 'price_per_km'):
                # Convertir Decimal en float pour le calcul
                km_rate = float(vehicle.price_per_km)
                total = km_rate * float(distance)
                return {
                    'total': total,
                    'details': {
                        'rate_per_km': km_rate,
                        'distance': float(distance),
                        'calculation': f"{km_rate} × {distance}"
                    }
                }
            
            return 0
        except (TypeError, ValueError, AttributeError) as e:
            logger.warning(f"Erreur de calcul de prix pour le véhicule {vehicle.id}: {str(e)}")
            return 0

    def get(self, request):
        try:
            # Récupérer les paramètres de recherche
            pricing_type = request.GET.get('pricing_type', 'distance')
            pickup_date = request.GET.get('pickup_date')
            pickup_lat = self._safe_float(request.GET.get('pickup_lat'))
            pickup_lng = self._safe_float(request.GET.get('pickup_lng'))
            dropoff_lat = self._safe_float(request.GET.get('dropoff_lat'))
            dropoff_lng = self._safe_float(request.GET.get('dropoff_lng'))
            hours = self._safe_float(request.GET.get('hours'))
            distance = self._safe_float(request.GET.get('distance'))
            passengers = self._safe_int(request.GET.get('passengers', 1))
            sort_by = request.GET.get('sort', 'price')

            # Validation de base
            if not pickup_date:
                raise ValidationError(_('Pickup date is required'))

            # Construire la requête de base
            query = Q(is_active=True, available=True, for_transfer=True)
            query &= Q(max_passengers__gte=passengers)

            # Ajouter des filtres selon le type de tarification
            if pricing_type == 'hourly':
                query &= Q(price_per_hour__isnull=False)
            else:  # distance
                if not all([pickup_lat, pickup_lng, dropoff_lat, dropoff_lng, distance]):
                    raise ValidationError(_('Pickup and drop-off locations are required for distance-based pricing'))
                query &= Q(price_per_km__isnull=False)# Récupérer et valider les paramètres de base
            pricing_type = request.GET.get('pricing_type', 'distance')
            passengers = self._safe_int(request.GET.get('passengers'), 1)
            luggage_pieces = self._safe_int(request.GET.get('luggage_pieces'), 0)
            luggage_weight = self._safe_float(request.GET.get('luggage_weight'), 0.0)
            pickup_date = request.GET.get('pickup_date')

            # Validation des entrées
            if not pickup_date:
                messages.error(request, _('Please specify a pickup date and time'))
                return redirect('transfer_search')

            # Validation selon le type de tarification
            hours = None
            distance = None
            
            if pricing_type == 'hourly':
                hours = self._safe_float(request.GET.get('hours'))
                if hours <= 0:
                    messages.error(request, _('Please specify a valid number of hours'))
                    return redirect('transfer_search')
            else:
                distance = self._safe_float(request.GET.get('distance'))
                if distance <= 0:
                    messages.error(request, _('Please specify a valid distance'))
                    return redirect('transfer_search')

            # Recherche des véhicules disponibles
            vehicles = AgencyCar.objects.filter(
                is_active=True,
                available=True,
                for_transfer=True
            ).select_related('agence', 'brand', 'car_model')

            # Filtrer par capacité
            vehicles = vehicles.filter(max_passengers__gte=passengers)

            # Filtrer par capacité de bagages si spécifié
            if luggage_pieces > 0:
                vehicles = vehicles.filter(luggage_capacity__gte=luggage_pieces)
            if luggage_weight > 0:
                vehicles = vehicles.filter(max_luggage_weight__gte=luggage_weight)

            # Calculer les prix pour chaque véhicule
            valid_vehicles = []
            for vehicle in vehicles:
                price_info = self._calculate_price(vehicle, pricing_type, hours, distance)
                if isinstance(price_info, dict) and price_info['total'] > 0:
                    vehicle.total_price = price_info['total']
                    vehicle.price_details = price_info['details']
                    valid_vehicles.append(vehicle)

            # Trier par prix
            valid_vehicles.sort(key=lambda x: x.total_price)

            # Pagination
            paginator = Paginator(valid_vehicles, self.items_per_page)
            page = request.GET.get('page', 1)
            
            try:
                vehicles_page = paginator.page(page)
            except PageNotAnInteger:
                vehicles_page = paginator.page(1)
            except EmptyPage:
                vehicles_page = paginator.page(paginator.num_pages)

            context = {
                'vehicles': vehicles_page,
                'search_params': {
                    'pricing_type': pricing_type,
                    'pickup_address': request.GET.get('pickup_address'),
                    'dropoff_address': request.GET.get('dropoff_address'),
                    'pickup_lat': request.GET.get('pickup_lat'),
                    'pickup_lng': request.GET.get('pickup_lng'),
                    'dropoff_lat': request.GET.get('dropoff_lat'),
                    'dropoff_lng': request.GET.get('dropoff_lng'),
                    'pickup_date': pickup_date,
                    'distance': distance,
                    'hours': hours,
                    'passengers': passengers,
                    'luggage_pieces': luggage_pieces,
                    'luggage_weight': luggage_weight
                }
            }

            return render(request, self.template_name, context)

        except Exception as e:
            logger.error(f"Erreur lors de la recherche de transfert : {str(e)}", exc_info=True)
            messages.error(request, _('An error occurred during the search. Please try again.'))
            return redirect('transfer_search')


class TransferBookingView(LoginRequiredMixin, View):
    template_name = 'transfer/booking_form.html'
    
    def get(self, request, vehicle_id):
        vehicle = get_object_or_404(AgencyCar, id=vehicle_id, is_active=True, available=True, for_transfer=True)
        pricing_type = request.GET.get('pricing_type', 'distance')
        
        context = {
            'vehicle': vehicle,
            'pickup_date': request.GET.get('pickup_date'),
            'hours': request.GET.get('hours'),
            'passengers': request.GET.get('passengers', 1),
            'pricing_type': pricing_type,
            'luggage_pieces': request.GET.get('luggage_pieces', 0),
            'luggage_weight': request.GET.get('luggage_weight', 0)
        }
        
        # Ajouter les champs de localisation uniquement pour la tarification par distance
        if pricing_type == 'distance':
            context.update({
                'pickup_address': request.GET.get('pickup_address'),
                'dropoff_address': request.GET.get('dropoff_address'),
                'pickup_lat': request.GET.get('pickup_lat'),
                'pickup_lng': request.GET.get('pickup_lng'),
                'dropoff_lat': request.GET.get('dropoff_lat'),
                'dropoff_lng': request.GET.get('dropoff_lng'),
                'distance': request.GET.get('distance')
            })
        
        # Calculer le prix estimé
        if context['pricing_type'] == 'hourly':
            hours = float(context['hours']) if context['hours'] else 1
            price_info = vehicle.calculate_transfer_price(hours=hours)
        else:
            distance = float(context['distance']) if context['distance'] else 0
            price_info = vehicle.calculate_transfer_price(distance=distance)
            
        if price_info:
            context['price_info'] = price_info
        
        return render(request, self.template_name, context)
    
    def post(self, request, vehicle_id):
        vehicle = get_object_or_404(AgencyCar, id=vehicle_id, is_active=True, available=True, for_transfer=True)
        
        try:
            # Valider les données de base
            pickup_date = request.POST.get('pickup_date')
            if not pickup_date:
                raise ValidationError(_('Pickup date is required'))

            passengers = int(request.POST.get('passengers', 1))
            if passengers > vehicle.max_passengers:
                raise ValidationError(_('Number of passengers exceeds vehicle capacity'))

            # Gérer les deux types de tarification
            pricing_type = request.POST.get('pricing_type', 'distance')
            price_info = None

            if pricing_type == 'hourly':
                duration_hours = float(request.POST.get('duration_hours', 0))
                if duration_hours <= 0:
                    raise ValidationError(_('Duration must be greater than zero'))
                price_info = vehicle.calculate_transfer_price(hours=duration_hours)
            else:
                # Tarification par distance
                distance = float(request.POST.get('distance', 0))
                if distance <= 0:
                    raise ValidationError(_('Distance must be greater than zero'))
                
                # Vérifier les coordonnées
                pickup_lat = request.POST.get('pickup_lat')
                pickup_lng = request.POST.get('pickup_lng')
                dropoff_lat = request.POST.get('dropoff_lat')
                dropoff_lng = request.POST.get('dropoff_lng')
                
                if not all([pickup_lat, pickup_lng, dropoff_lat, dropoff_lng]):
                    raise ValidationError(_('Pickup and drop-off locations are required'))
                
                price_info = vehicle.calculate_transfer_price(distance=distance)

            if not price_info or not price_info.get('total_price'):
                raise ValidationError(_('Could not calculate price'))

            # Créer la réservation
            booking = TransferBooking(
                vehicle=vehicle,
                user=request.user,
                pickup_date=pickup_date,
                pricing_type=pricing_type,
                passengers_count=passengers,
                total_price=Decimal(str(price_info['total_price']))
            )

            # Ajouter les champs spécifiques selon le type de tarification
            if pricing_type == 'hourly':
                booking.duration_hours = duration_hours
            else:
                booking.distance = distance
                booking.pickup_location = Point(float(pickup_lng), float(pickup_lat))
                booking.dropoff_location = Point(float(dropoff_lng), float(dropoff_lat))
                booking.pickup_address = request.POST.get('pickup_address')
                booking.dropoff_address = request.POST.get('dropoff_address')

            # Ajouter les champs optionnels
            if 'luggage_pieces' in request.POST:
                booking.luggage_pieces = int(request.POST.get('luggage_pieces'))
            if 'luggage_weight' in request.POST:
                booking.luggage_weight = Decimal(request.POST.get('luggage_weight'))
            if 'notes' in request.POST:
                booking.notes = request.POST.get('notes')

            booking.save()
            
            messages.success(request, _('Your transfer booking has been confirmed'))
            return redirect('transfer_booking_detail', booking_id=booking.id)

        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            logger.error(f'Error creating transfer booking: {str(e)}')
            messages.error(request, _('An error occurred while processing your booking'))
            
        return render(request, self.template_name, {
            'vehicle': vehicle,
            'form_data': request.POST
        })


class TransferBookingDetailView(LoginRequiredMixin, View):
    template_name = 'transfer/booking_detail.html'
    
    def get(self, request, booking_id):
        booking = get_object_or_404(
            TransferBooking.objects.select_related('vehicle', 'user'),
            id=booking_id
        )
        
        # Vérifier que l'utilisateur est autorisé à voir cette réservation
        if not (request.user == booking.user or request.user.is_staff or has_agency_permission(request.user, booking.vehicle.agence)):
            raise PermissionDenied
        
        context = {
            'booking': booking,
            'vehicle': booking.vehicle,
            'status_history': booking.status_history.all().order_by('-created_at') if hasattr(booking, 'status_history') else None,
        }
        
        return render(request, self.template_name, context)

class UserTransferBookingsView(LoginRequiredMixin, ListView):
    template_name = 'transfer/user_bookings.html'
    context_object_name = 'bookings'
    paginate_by = 10

    def get_queryset(self):
        return TransferBooking.objects.filter(
            user=self.request.user
        ).select_related(
            'vehicle__brand',
            'vehicle__car_model',
            'vehicle__agence'
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_bookings = TransferBooking.objects.filter(user=self.request.user)
        
        # Ajouter les statistiques
        context['pending_count'] = user_bookings.filter(status='pending').count()
        context['confirmed_count'] = user_bookings.filter(status='confirmed').count()
        context['completed_count'] = user_bookings.filter(status='completed').count()
        context['cancelled_count'] = user_bookings.filter(status='cancelled').count()
        
        return context

class TransferBookingCancelView(LoginRequiredMixin, View):
    def post(self, request, booking_id):
        try:
            booking = get_object_or_404(TransferBooking, id=booking_id, user=request.user)
            
            if booking.status != 'pending':
                return JsonResponse({
                    'success': False,
                    'message': _('Only pending bookings can be cancelled')
                }, status=400)
            
            booking.status = 'cancelled'
            booking.save()
            
            messages.success(request, _('Your transfer booking has been cancelled'))
            return JsonResponse({'success': True})
            
        except Exception as e:
            logger.error(f'Error cancelling transfer booking: {str(e)}')
            return JsonResponse({
                'success': False,
                'message': _('An error occurred while cancelling your booking')
            }, status=500)