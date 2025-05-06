from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
import json
from datetime import datetime
import logging

from cars.models import TransferVehicle, TransferBooking, AgencyCar
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
    
    def get(self, request):
        try:
            # Récupération des paramètres de recherche
            pickup_lat = float(request.GET.get('pickup_lat'))
            pickup_lng = float(request.GET.get('pickup_lng'))
            dropoff_lat = float(request.GET.get('dropoff_lat'))
            dropoff_lng = float(request.GET.get('dropoff_lng'))
            pickup_point = Point(pickup_lng, pickup_lat, srid=4326)
            dropoff_point = Point(dropoff_lng, dropoff_lat, srid=4326)
            
            distance = float(request.GET.get('distance', 0))
            passengers = int(request.GET.get('passengers', 1))
            luggage_pieces = int(request.GET.get('luggage_pieces', 0))
            luggage_weight = float(request.GET.get('luggage_weight', 0))
            pickup_date = request.GET.get('pickup_date')

            # Recherche des véhicules disponibles
            vehicles = AgencyCar.objects.filter(
                is_active=True,
                available=True,
                for_transfer=True,
                max_passengers__gte=passengers,
                max_luggage_pieces__gte=luggage_pieces,
                max_luggage_weight__gte=luggage_weight
            ).select_related('agence', 'brand', 'car_model')
            
            # Calculer les prix pour chaque véhicule
            for vehicle in vehicles:
                # Prix basé sur la distance
                price_by_distance = vehicle.price_per_km * distance if vehicle.price_per_km else 0
                
                # Prix basé sur la durée estimée (1h par 50km en moyenne)
                estimated_duration = max(1, distance / 50)
                price_by_hour = vehicle.price_per_hour * estimated_duration if vehicle.price_per_hour else 0
                
                # Prendre le prix le plus élevé pour garantir la rentabilité
                vehicle.total_price = max(price_by_distance, price_by_hour)
                vehicle.estimated_duration = estimated_duration
                
                # Informations supplémentaires pour l'affichage
                vehicle.price_details = {
                    'by_distance': price_by_distance,
                    'by_hour': price_by_hour,
                    'final_price': vehicle.total_price,
                    'distance': distance,
                    'duration': estimated_duration
                }
            
            # Trier par prix
            vehicles = sorted(vehicles, key=lambda x: x.total_price)
            
            # Pagination
            paginator = Paginator(vehicles, self.items_per_page)
            page = request.GET.get('page', 1)
            try:
                vehicles_page = paginator.page(page)
            except:
                vehicles_page = paginator.page(1)
            
            context = {
                'vehicles': vehicles_page,
                'search_params': {
                    'pickup_address': request.GET.get('pickup_address'),
                    'dropoff_address': request.GET.get('dropoff_address'),
                    'pickup_date': pickup_date,
                    'distance': distance,
                    'passengers': passengers,
                    'luggage_pieces': luggage_pieces,
                    'luggage_weight': luggage_weight
                }
            }
            
            return render(request, self.template_name, context)
            
        except (ValueError, TypeError) as e:
            messages.error(request, _('Invalid search parameters. Please check your inputs.'))
            logger.error(f"Error in transfer search: {str(e)}")
            return redirect('transfer_search')
        except Exception as e:
            messages.error(request, _('An error occurred during the search.'))
            logger.error(f"Unexpected error in transfer search: {str(e)}")
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