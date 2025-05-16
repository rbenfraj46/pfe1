from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.html import strip_tags
from home.tokens import account_activation_token

def send_mail_verification(request, user):
    """
    Send HTML mail verification email
    """
    current_site = get_current_site(request)
    mail_subject = _('Activate your account.')
    
    # Render HTML version
    html_message = render_to_string('email_template.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'scheme': request.scheme,
    })
    
    # Create the email message
    email = EmailMultiAlternatives(
        subject=mail_subject,
        body='Please enable HTML to view this email',
        from_email=settings.NO_REPLY_EMAIL_ADRESS,
        to=[user.email]
    )
    
    # Attach HTML version
    email.attach_alternative(html_message, "text/html")
    email.send()

def send_mail_reset_password(request, user):
    """
    Send HTML password reset email
    """
    subject = _("Password Reset Requested")
    current_site = get_current_site(request)
    
    # Render HTML version
    html_message = render_to_string("password_reset_email.html", {
        "email": user.email,
        'domain': current_site.domain,
        'site_name': 'TunCar',
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "user": user,
        'token': default_token_generator.make_token(user),
        'protocol': request.scheme,
    })
    
    # Create the email message
    email = EmailMultiAlternatives(
        subject=subject,
        body='Please enable HTML to view this email',
        from_email=settings.NO_REPLY_EMAIL_ADRESS,
        to=[user.email]
    )
    
    # Attach HTML version
    email.attach_alternative(html_message, "text/html")
    email.send()

def send_mail_verification_agency(request, agence):
    """
    Send HTML mail verification email for agency
    """
    current_site = get_current_site(request)
    mail_subject = _('Activate your agency.')
    
    # Render HTML version
    html_message = render_to_string('email_template_agency.html', {
        'agence': agence,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(agence.pk)),
        'token': account_activation_token.make_token(agence),
        'scheme': request.scheme,
    })
    
    # Create the email message
    email = EmailMultiAlternatives(
        subject=mail_subject,
        body='Please enable HTML to view this email',
        from_email=settings.NO_REPLY_EMAIL_ADRESS,
        to=[agence.email]
    )
    
    # Attach HTML version
    email.attach_alternative(html_message, "text/html")
    email.send()

def send_car_rental_notification(reservation, notification_type, **kwargs):
    current_site = kwargs.get('request') and get_current_site(kwargs['request']) or None

def send_transfer_notification(booking, notification_type, **kwargs):
    """
    Send notification emails for transfer bookings
    notification_type can be: 'new', 'confirmed', 'cancelled', 'completed'
    """
    current_site = kwargs.get('request') and get_current_site(kwargs['request']) or None
    
    subject_map = {
        'new': _('New Transfer Booking Confirmation'),
        'confirmed': _('Your Transfer Booking has been Confirmed'),
        'cancelled': _('Transfer Booking Cancellation'),
        'completed': _('Transfer Service Completed'),
        'agency_completed': _('Transfer Service Completed - Agency Notification'),
    }
    
    template_map = {
        'new_user': 'transfer/email/booking_pending_user.html',
        'new_agency': 'transfer/email/booking_pending_agency.html',
        'confirmed': 'transfer/email/booking_confirmed.html',
        'cancelled': 'transfer/email/booking_cancelled.html',
        'completed': 'transfer/email/service_completed.html',
        'agency_completed': 'transfer/email/agency_completed.html',
    }
    
    subject = subject_map.get(notification_type, _('Transfer Booking Update'))
    
    # Ensure dates are timezone aware
    from django.utils import timezone
    if booking.pickup_date and timezone.is_naive(booking.pickup_date):
        booking.pickup_date = timezone.make_aware(booking.pickup_date)
    
    # Add static support for email templates
    from django.contrib.staticfiles import finders
    from django.templatetags.static import static
    
    # Render HTML version
    html_message = render_to_string(template_map.get(notification_type), {
        'booking': booking,
        'domain': current_site.domain if current_site else 'tuncar.com',
        'site_name': 'TunCar',
        'protocol': kwargs.get('request').scheme if kwargs.get('request') else 'https',
        'static': static,
    })
    
    # Create the email message
    email = EmailMultiAlternatives(
        subject=subject,
        body='Please enable HTML to view this email',
        from_email=settings.NO_REPLY_EMAIL_ADRESS,
        to=[booking.user.email]
    )
    
    def send_email(recipient, is_agency=False, template_override=None):
        # Créer un contexte spécifique pour le destinataire
        context = {
            'booking': booking,
            'domain': current_site.domain if current_site else 'tuncar.com',
            'site_name': 'TunCar',
            'protocol': kwargs.get('request').scheme if kwargs.get('request') else 'https',
            'static': static,
            'is_agency': is_agency
        }
        
        # Rendre le template avec le contexte spécifique
        email_html = render_to_string(template_map.get(notification_type), context)
        
        # Créer et envoyer l'email
        msg = EmailMultiAlternatives(
            subject=subject,
            body='Please enable HTML to view this email',
            from_email=settings.NO_REPLY_EMAIL_ADRESS,
            to=[recipient]
        )
        msg.attach_alternative(email_html, "text/html")
        msg.send()

    # Envoyer les emails selon le type de notification
    if notification_type == 'new':
        # Envoyer email au client avec template spécifique client
        send_email(booking.user.email, is_agency=False, template_override='new_user')
        # Envoyer email à l'agence avec template spécifique agence
        send_email(booking.vehicle.agency.email, is_agency=True, template_override='new_agency')
        # Si un admin est configuré, lui envoyer aussi la notification
        admin_email = getattr(settings, 'TRANSFER_ADMIN_EMAIL', None)
        if admin_email:
            send_email(admin_email, is_agency=True, template_override='new_agency')
    elif notification_type == 'agency_completed':
        send_email(booking.vehicle.agency.email, is_agency=True)
    else:
        send_email(booking.user.email, is_agency=False)
    
    # Attach HTML version
    email.attach_alternative(html_message, "text/html")
    email.send()
    domain = current_site and current_site.domain or 'localhost:8000'
    scheme = kwargs.get('request') and kwargs['request'].scheme or 'http'
    
    templates = {
        'request': 'email/rental_request.html',
        'approved': 'email/rental_approved.html',
        'cancelled': 'email/rental_cancelled.html'
    }

    subjects = {
        'request': _('New Car Rental Request'),
        'approved': _('Your Car Rental Request has been Approved'),
        'cancelled': _('Car Rental Reservation Cancelled')
    }

    recipient = reservation.car.agence.email if notification_type == 'request' else reservation.user.email

    # Base context avec tous les paramètres nécessaires
    context = {
        'scheme': scheme,
        'domain': domain,
        'user_name': reservation.user.get_full_name() or reservation.user.username,
        'car_info': f"{reservation.car.brand.name} {reservation.car.car_model.name}",
        'car_image': reservation.car.image.url if reservation.car.image else None,
        'agency_name': reservation.car.agence.agency_name,
        'start_date': reservation.start_date,
        'end_date': reservation.end_date,
        'total_price': reservation.total_price,
        'currency': 'TND',
        'status': reservation.status,
        'status_text': dict(reservation.STATUS_CHOICES)[reservation.status],
    }

    # Ajout de contexte spécifique selon le type de notification
    if notification_type == 'request':
        context.update({
            'admin_url': f"{scheme}://{domain}/admin/cars/carreservation/{reservation.id}/change/"
        })
    elif notification_type == 'approved':
        context.update({
            'security_deposit': reservation.car.security_deposit,
            'payment_url': f"{scheme}://{domain}/reservations/{reservation.id}/pay/"
        })
    elif notification_type == 'cancelled':
        context.update({
            'cancellation_reason': kwargs.get('cancellation_reason'),
            'support_url': f"{scheme}://{domain}/contact/",
            'search_url': f"{scheme}://{domain}/cars/search/"
        })

    # Rendu du template HTML
    html_message = render_to_string(templates[notification_type], context)
    
    # Création du message email
    email = EmailMultiAlternatives(
        subject=subjects[notification_type],
        body=strip_tags(html_message),  # Version texte
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient]
    )
    
    # Ajout de la version HTML
    email.attach_alternative(html_message, "text/html")
    email.send()
