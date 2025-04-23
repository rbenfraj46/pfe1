from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.views.generic import ListView
from django.db.models import Count, Q
from django.core.exceptions import PermissionDenied
import decimal
import logging

logger = logging.getLogger(__name__)

from cars.models import CarReservation
from home.models import Agences
from home.views.agences import has_agency_permission

class RentalStatusUpdateView(LoginRequiredMixin, View):
    def get(self, request, reservation_id):
        reservation = get_object_or_404(CarReservation, id=reservation_id)
        return redirect('agency_rentals', agency_id=reservation.car.agence.id)

    def post(self, request, reservation_id):
        try:
            # Vérification de l'authentification
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False, 
                    'message': _('Authentication required')
                }, status=401)
            
            # Récupération et validation de la réservation
            try:
                reservation = CarReservation.objects.select_related(
                    'car__agence'
                ).get(id=reservation_id)
            except CarReservation.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': _('Reservation not found')
                }, status=404)
            
            # Vérification des permissions
            if not (reservation.car.agence.creator == request.user or 
                    has_agency_permission(request.user, reservation.car.agence.id, 'edit')):
                return JsonResponse({
                    'success': False,
                    'message': _('You do not have permission to update this rental')
                }, status=403)

            # Validation des données reçues
            requested_status = request.POST.get('status')
            reason = request.POST.get('reason')
            payment_amount = request.POST.get('payment_amount')

            if not requested_status or not reason:
                return JsonResponse({
                    'success': False,
                    'message': _('Status and reason are required')
                }, status=400)

            # Validation de la transition de statut
            if not reservation.can_transition_to(requested_status):
                return JsonResponse({
                    'success': False,
                    'message': _('Invalid status transition from {current} to {requested}').format(
                        current=reservation.status,
                        requested=requested_status
                    )
                }, status=400)

            # Traitement du paiement si fourni
            if payment_amount:
                try:
                    payment_amount = decimal.Decimal(payment_amount)
                    if payment_amount < 0:
                        raise ValueError(_('Payment amount cannot be negative'))
                    reservation.update_payment_status(payment_amount)
                except (decimal.InvalidOperation, ValueError) as e:
                    return JsonResponse({
                        'success': False,
                        'message': str(e) or _('Invalid payment amount')
                    }, status=400)

            # Mise à jour du statut
            reservation.status = requested_status
            reservation.rejection_reason = reason
            reservation.save()

            # Envoi des notifications
            try:
                from home.mail_util import send_car_rental_notification
                send_car_rental_notification(reservation, requested_status, reason)
            except Exception as e:
                logger.warning(f"Failed to send notification email: {str(e)}")

            return JsonResponse({
                'success': True,
                'status': reservation.status,
                'payment_status': reservation.payment_status,
                'amount_paid': float(reservation.amount_paid),
                'total_price': float(reservation.total_price),
                'message': _('Status updated successfully')
            })

        except Exception as e:
            logger.error(f"Error updating rental status: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'message': _('An unexpected error occurred. Please try again.')
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