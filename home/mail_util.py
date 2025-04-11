from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
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
