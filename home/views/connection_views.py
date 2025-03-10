from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.urls.base import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic.base import TemplateView
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.conf import settings

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView

from django.utils.translation import gettext_lazy as _

from axes.utils import reset_request
from axes.middleware import AxesMiddleware

from home.forms.login_forms import AxesLoginCaptchaForm
from home.forms.login_forms import AxesLoginForm
from home.forms.login_forms import ResetPasswordForm

from home.mail_util import send_mail_verification
from home.mail_util import send_mail_reset_password
from home.models import Devise
from home.models import UserPreference
from home.views.index import IndexView


def middleware_call_subclass(self, request):
    response = self.get_response(request)
    return response

AxesMiddleware.__call__ = middleware_call_subclass

User = get_user_model()


class Login(IndexView):
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('index'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        devise = None
        if not getattr(self, 'stateless_info', {}):
            self.stateless_info = {}
            self.stateless_info['devises'] = Devise.objects.filter(is_active=True).order_by('order_key')
            self.stateless_info['default_devise'] = Devise.objects.get(name='TND')

        if self.request.session.get('user_devise', None):
            devise = Devise.objects.get(name=self.request.session.get('user_devise', None))

        elif self.request.user.is_authenticated:
            #get devise from preference:
            prefs = UserPreference.objects.filter(user=self.request.user).first()
            if prefs:
                devise = prefs.devise


        if not devise:
            devise = self.stateless_info['default_devise']

        context['devise'] = devise
        context['devises'] = self.stateless_info['devises']
        return context

class login_view(Login):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['state'] = ''
        context['action_name'] = _('Login')
        return context

    def post(self, request, *args, **kwargs):
        # profile_is_new = Profile.objects.get_or_create(user=user)
        username = ""
        password = ""
        state = ""
        if request.session.get('need_captcha', False):
            form = AxesLoginCaptchaForm(request.POST)
        else:
            form = AxesLoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username').lower()
            password = form.cleaned_data.get('password')
            if 'need_captcha' in request.session:
                del(request.session['need_captcha'])
                reset_request(request)

            user = authenticate(request=request, username=username, password=password)
            if not user:
                try:
                    # get username from db if the passed username is email
                    _username = User.objects.get(email=username).username
                    user = authenticate(request=request, username=_username, password=password)
                except User.DoesNotExist:
                    pass

            if user is not None:
                if not user.is_active:
                        state = _("Your account is deactivated. Please contact support!!")
                elif not user.is_mail_verified:
                    request.session['user_mail_verification'] = user.pk
                    return redirect(reverse('mail_not_confirmed'))
                else:
                    login(request, user)
                    if form.cleaned_data.get('remember_me', False):
                        request.session.set_expiry(0)
                    else:
                        request.session.set_expiry(None)
                    request.session.modified = True

                    nxt = request.GET.get("next", None)
                    if nxt is None:
                        return redirect(settings.LOGIN_REDIRECT_URL)
                    elif not url_has_allowed_host_and_scheme(request.GET['next'], None):
                        return redirect(settings.LOGIN_REDIRECT_URL)
                    else:
                        return redirect(nxt)
            else:
                if request.axes_locked_out:
                    form = AxesLoginCaptchaForm()
                    request.session['need_captcha'] = True
                    state = _("You must fill the captcha.")
                else:
                    form = AxesLoginForm()
                    state = _("Invalid Credentials.")
        return render(request, 'login.html', {'state': state,
                                              'username': username,
                                              'form': form,
                                              'action_name': _('Login')},
                                              status=200)

class ForgetPassword(Login):

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email', '')
        form = ResetPasswordForm(request.POST)
        reset_msg = None
        if form.is_valid():
            email = form.cleaned_data.get('email')
            users = User.objects.filter(email__iexact=email).all()
            if len(users) == 1:
                # send mail
                send_mail_reset_password(request, users[0])
                messages.success(request, _('We have emailed you instructions for setting your password. You should receive the email shortly!'))
                return redirect(reverse('index'))

            else:
                reset_msg = _('No user with this email !!')

        return render(request, 'login.html', {'reset_msg': reset_msg,
                                              'email': email,
                                              'form_send': form,
                                              'action_name': _('Login')},
                                              status=200)


class ResetDoneView(Login):
    def get(self, request, *args, **kwargs):
        messages.success(request, _('Password changed successfully.'))
        return redirect(reverse('index'))


class ChangePasswordView(LoginRequiredMixin, PasswordChangeView, Login):
    template_name = 'change_password.html'


class MailNotConfirmedView(Login):
    template_name = "mail_not_confirmed.html"

    def get_context_data(self, **kwargs):
        user = None
        context = super().get_context_data(**kwargs)
        # get the user:
        user_pk = self.request.session.get('user_mail_verification', None)
        if user_pk:
            user_pk = int(user_pk)
            try:
                # get username from db if the passed username is email
                user = User.objects.get(id=user_pk)
            except User.DoesNotExist:
                user = None

        context['user_rq'] = user
        return context

    def post(self, request, *args, **kwargs):

        context = self.get_context_data()
        user = context['user_rq']

        messages.success(request, _('Please check your mail box and hit the mail verification.'))
        send_mail_verification(request, user)

        return redirect(reverse('index'))
