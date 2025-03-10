from django.shortcuts import render
from django.shortcuts import redirect
from django.urls.base import reverse

from home.forms.registration_forms import RegistrationForm
from django.utils.translation import gettext_lazy as _

from django.contrib import messages


from django.utils.http import urlsafe_base64_decode

from django.utils.encoding import force_str

from django.contrib.auth import get_user_model

from django.conf import settings

from home.tokens import account_activation_token
from home.views.connection_views import Login

from home.mail_util import send_mail_verification

User = get_user_model()


class RegisterationView(Login):
    template_name =  "login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['state'] = ''
        context['action_name'] = _('Register')
        return context

    def post(self, request, *args, **kwargs):
        """
        test data
        """
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            if settings.SEND_CONFIRMATION_MAIL:
                send_mail_verification(request, user)

            messages.success(request, _('User created Successfully. Please check your mail box and hit the mail verification.'))
            return redirect(reverse('index'))
        else:
            return render(request, 'login.html', {'form_reg': form, 'action_name': _('Login')}, status=200)

def activate(request, uidb64, token):

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk = uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.is_mail_verified = True
        user.save()
        messages.success(request, _('Your mail address is successfully activated.'))
        return redirect(reverse('index'))
    else :
        messages.success(request, _('This link is dead. Try to generate another link.'))
        return redirect(reverse('index'))

