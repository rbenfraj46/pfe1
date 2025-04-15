from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.views.generic import ListView
from django.db.models import Count, Q
from django.core.exceptions import PermissionDenied

from cars.models import CarReservation, RentalStatusChange
from home.models import Agences
from home.views.agences import has_agency_permission

class RentalStatusUpdateView(LoginRequiredMixin, View):
    def get(self, request, reservation_id):
        # Get the reservation to find the agency ID
        reservation = get_object_or_404(CarReservation, id=reservation_id)
        return redirect('agency_rentals', agency_id=reservation.car.agence.id)

    def post(self, request, reservation_id):
        # Get the reservation and check permissions
        reservation = get_object_or_404(CarReservation, id=reservation_id)
        agency = reservation.car.agence
        
        # Check if user has permission to update this rental
        if not (agency.creator == request.user or 
                has_agency_permission(request.user, agency.id, 'edit')):
            return JsonResponse({
                'success': False,
                'message': _('You do not have permission to update this rental')
            }, status=403)
        
        requested_status = request.POST.get('status')
        reason = request.POST.get('reason')
        
        if not requested_status or not reason:
            return JsonResponse({
                'success': False,
                'message': _('Status and reason are required')
            }, status=400)
            
        try:
            status_change = reservation.request_status_change(
                requested_status=requested_status,
                reason=reason,
                requested_by=request.user
            )
            
            if status_change.status == 'approved':
                messages.success(request, _('Rental status updated successfully'))
                return JsonResponse({
                    'success': True,
                    'status': requested_status,
                    'auto_approved': True
                })
            else:
                messages.info(
                    request, 
                    _('Status change request submitted for admin review')
                )
                return JsonResponse({
                    'success': True,
                    'status': reservation.status,
                    'auto_approved': False,
                    'pending_review': True
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)

class AgencyRentalsView(LoginRequiredMixin, ListView):
    template_name = 'rental/agency_rentals.html'
    context_object_name = 'rentals'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        self.agency = get_object_or_404(Agences, id=self.kwargs.get('agency_id'))
        if not (self.agency.creator == request.user or 
                has_agency_permission(request.user, self.agency.id, 'view')):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return CarReservation.objects.filter(
            car__agence=self.agency
        ).select_related(
            'car__brand',
            'car__car_model',
            'car__agence',
            'user'
        ).prefetch_related(
            'status_changes'
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rentals = self.get_queryset()
        
        stats = rentals.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            approved=Count('id', filter=Q(status='approved')),
            rejected=Count('id', filter=Q(status='rejected'))
        )
        
        context.update(stats)
        context['agency'] = self.agency
        return context