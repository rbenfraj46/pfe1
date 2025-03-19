from django.conf import settings

from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator



from home.tokens import account_activation_token



def send_mail_verification(request, user):
    """
    send mail verification mail
    """
    current_site = get_current_site(request)
    mail_subject = _('Activate your account.')
    message = render_to_string('email_template.html', {
       'user': user,
       'domain': current_site.domain,
       'uid': urlsafe_base64_encode(force_bytes(user.pk)),
       'token': account_activation_token.make_token(user),
       'scheme': request.scheme,
    })
    to_email = user.email
    send_mail(mail_subject, message, settings.NO_REPLY_EMAIL_ADRESS , [to_email])


def send_mail_reset_password(request, user):
    subject = _("Password Reset Requested")
    current_site = get_current_site(request)
    email_template_name = "password_reset_email.html"
    c = {
        "email": user.email,
        'domain': current_site.domain,
        'site_name': 'TunCar',
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "user": user,
        'token': default_token_generator.make_token(user),
        'protocol': request.scheme,
    }
    email = render_to_string(email_template_name, c)
    send_mail(subject, email, settings.NO_REPLY_EMAIL_ADRESS , [user.email])


def send_mail_verification_agency(request, agence):
    """
    send mail verification mail for agency
    """
    current_site = get_current_site(request)
    mail_subject = _('Activate your agency.')
    message = render_to_string('email_template_agency.html', {
       'agence': agence,
       'domain': current_site.domain,
       'uid': urlsafe_base64_encode(force_bytes(agence.pk)),
       'token': account_activation_token.make_token(agence),
       'scheme': request.scheme,
    })
    to_email = agence.email
    send_mail(mail_subject, message, settings.NO_REPLY_EMAIL_ADRESS, [to_email])
