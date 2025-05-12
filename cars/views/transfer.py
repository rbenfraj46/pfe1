from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.gis.geos import Point
from django.db.models import Q
import logging
from datetime import datetime
from decimal import Decimal

from cars.models import AgencyCar, TransferVehicle, TransferBooking
from home.models import Agences
from home.views.agences import has_agency_permission

logger = logging.getLogger(__name__)

class TransferVehicleListView(LoginRequiredMixin, ListView):
    template_name = 'transfer/agency_vehicles.html'
    context_object_name = 'vehicles'
    paginate_by = 10

    def get_queryset(self):
        self.agency = get_object_or_404(Agences, id=self.kwargs['agency_id'])
        if not (self.agency.creator == self.request.user or 
                has_agency_permission(self.request.user, self.agency.id, 'view')):
            raise PermissionDenied
        
        return TransferVehicle.objects.filter(
            agence=self.agency,
            is_active=True
        ).order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['agency'] = self.agency
        return context

class TransferVehicleCreateView(LoginRequiredMixin, View):
    template_name = 'transfer/vehicle_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.agency = get_object_or_404(Agences, id=kwargs['agency_id'])
        if not (self.agency.creator == request.user or 
                has_agency_permission(request.user, self.agency.id, 'add')):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            'agency': self.agency
        })

    def post(self, request, *args, **kwargs):
        try:
            vehicle = TransferVehicle(
                agence=self.agency,
                vehicle_type=request.POST['vehicle_type'],
                brand_id=request.POST['brand'],
                model=request.POST['model'],
                capacity=request.POST['capacity'],
                hourly_rate=request.POST['hourly_rate'],
                minimum_hours=request.POST['minimum_hours'],
                driver_name=request.POST['driver_name'],
                driver_phone=request.POST['driver_phone'],
                driver_license_number=request.POST['driver_license_number'],
                driver_experience_years=request.POST['driver_experience_years'],
                driver_languages=request.POST['driver_languages']
            )
            
            if 'image' in request.FILES:
                vehicle.image = request.FILES['image']
                
            vehicle.save()
            messages.success(request, _('Transfer vehicle added successfully'))
            return redirect('agency_transfer_vehicles', agency_id=self.agency.id)
            
        except Exception as e:
            messages.error(request, str(e))
            return render(request, self.template_name, {
                'agency': self.agency
            })

class TransferBookingListView(LoginRequiredMixin, ListView):
    template_name = 'transfer/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 10

    def get_queryset(self):
        status_filter = self.request.GET.get('status')
        bookings = TransferBooking.objects.filter(
            user=self.request.user
        ).select_related('vehicle', 'vehicle__agence')
        
        if status_filter:
            bookings = bookings.filter(status=status_filter)
            
        return bookings.order_by('-created_at')

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

    def get(self, request):
        try:
            # Récupérer et valider les paramètres de base
            pricing_type = request.GET.get('pricing_type', 'distance')
            passengers = self._safe_int(request.GET.get('passengers'), 1)
            luggage_pieces = self._safe_int(request.GET.get('luggage_pieces'), 0)
            luggage_weight = self._safe_float(request.GET.get('luggage_weight'), 0.0)
            pickup_date = request.GET.get('pickup_date')

            # Validation de la date
            if not pickup_date:
                messages.error(request, _('Please select a pickup date and time'))
                return redirect('transfer_search')

            # Base query pour les véhicules
            vehicles = AgencyCar.objects.filter(
                is_active=True,
                available=True,
                for_transfer=True
            ).select_related('agence', 'brand', 'car_model')

            # Filtrer par capacité et bagages
            vehicles = vehicles.filter(max_passengers__gte=passengers)
            if luggage_pieces > 0:
                vehicles = vehicles.filter(max_luggage_pieces__gte=luggage_pieces)
            if luggage_weight > 0:
                vehicles = vehicles.filter(max_luggage_weight__gte=luggage_weight)

            # Variables pour le contexte
            distance = None
            hours = None

            if pricing_type == 'hourly':
                hours = self._safe_float(request.GET.get('hours'))
                if hours <= 0:
                    messages.error(request, _('Please enter a valid number of hours'))
                    return redirect('transfer_search')

                # Calculer le prix pour chaque véhicule
                for vehicle in vehicles:
                    if not vehicle.price_per_hour:
                        continue
                    
                    vehicle.total_price = float(vehicle.price_per_hour) * hours
                    vehicle.price_details = {
                        'by_hour': vehicle.total_price,
                        'hours': hours,
                        'rate_per_hour': float(vehicle.price_per_hour),
                        'final_price': vehicle.total_price
                    }

            else:  # pricing_type == 'distance'
                # Validation des coordonnées
                pickup_lat = self._safe_float(request.GET.get('pickup_lat'))
                pickup_lng = self._safe_float(request.GET.get('pickup_lng'))
                dropoff_lat = self._safe_float(request.GET.get('dropoff_lat'))
                dropoff_lng = self._safe_float(request.GET.get('dropoff_lng'))
                distance = self._safe_float(request.GET.get('distance'))

                if not all([pickup_lat, pickup_lng, dropoff_lat, dropoff_lng]):
                    messages.error(request, _('Please select both pickup and drop-off locations'))
                    return redirect('transfer_search')

                if distance <= 0:
                    messages.error(request, _('Invalid distance between locations'))
                    return redirect('transfer_search')

                # Calculer le prix pour chaque véhicule
                for vehicle in vehicles:
                    if not vehicle.price_per_km or not vehicle.price_per_hour:
                        continue
                        
                    # Prix basé sur la distance
                    price_by_distance = float(vehicle.price_per_km) * distance
                    
                    # Prix basé sur la durée estimée (1h par 50km en moyenne)
                    estimated_duration = max(1, distance / 50)
                    price_by_hour = float(vehicle.price_per_hour) * estimated_duration
                    
                    # Prendre le prix le plus élevé
                    vehicle.total_price = max(price_by_distance, price_by_hour)
                    vehicle.price_details = {
                        'by_distance': price_by_distance,
                        'by_hour': price_by_hour,
                        'distance': distance,
                        'duration': estimated_duration,
                        'final_price': vehicle.total_price
                    }

            # Filtrer les véhicules sans prix et trier
            vehicles = [v for v in vehicles if hasattr(v, 'total_price') and v.total_price > 0]
            vehicles.sort(key=lambda x: x.total_price)

            # Pagination
            paginator = Paginator(vehicles, self.items_per_page)
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
        vehicle = get_object_or_404(TransferVehicle, id=vehicle_id)
        return render(request, self.template_name, {
            'vehicle': vehicle,
            'pickup_address': request.GET.get('pickup_address'),
            'dropoff_address': request.GET.get('dropoff_address'),
            'pickup_date': request.GET.get('pickup_date'),
            'passengers': request.GET.get('passengers'),
            'duration': request.GET.get('duration')
        })
    
    def post(self, request, vehicle_id):
        vehicle = get_object_or_404(TransferVehicle, id=vehicle_id)
        try:
            # Create pickup and dropoff points
            pickup_point = Point(
                float(request.POST['pickup_lng']),
                float(request.POST['pickup_lat']),
                srid=4326
            )
            dropoff_point = Point(
                float(request.POST['dropoff_lng']),
                float(request.POST['dropoff_lat']),
                srid=4326
            )
            
            # Parse pickup datetime
            pickup_date = datetime.strptime(
                request.POST['pickup_date'],
                '%Y-%m-%dT%H:%M'
            )
            
            # Create booking
            booking = TransferBooking.objects.create(
                vehicle=vehicle,
                user=request.user,
                pickup_location=pickup_point,
                dropoff_location=dropoff_point,
                pickup_address=request.POST['pickup_address'],
                dropoff_address=request.POST['dropoff_address'],
                pickup_date=pickup_date,
                estimated_duration=int(request.POST['duration']),
                passengers_count=int(request.POST['passengers']),
                notes=request.POST.get('notes'),
                total_price=vehicle.hourly_rate * int(request.POST['duration'])
            )
            
            messages.success(request, _('Transfer booking created successfully'))
            return redirect('transfer_booking_details', booking_id=booking.id)
            
        except Exception as e:
            messages.error(request, str(e))
            return render(request, self.template_name, {
                'vehicle': vehicle
            })