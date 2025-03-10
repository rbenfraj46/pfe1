from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib import messages
from django.http import HttpResponseRedirect

from django.urls.base import reverse
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


from django.views.generic.base import TemplateView

from home.models import Devise
from home.models import MailSubscription
from home.models import UserPreference

from home.forms.index_forms import DeviseForm, NewsLetterSubscription
from django.contrib.auth.mixins import LoginRequiredMixin


User = get_user_model()

# Create your views here.

class PostView(TemplateView):
    template_name =  "index.html"

    def get(self, request, *args, **kwargs):
        raise Http404()


class IndexView(TemplateView):
    template_name =  "index.html"

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

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class DeviseView(PostView):

    def post(self, request, *args, **kwargs):
        # check devise exist
        form = DeviseForm(request.POST)
        if not form.is_valid():
            raise Http404()
        devise = Devise.objects.filter(name=form.cleaned_data.get('devise')).first()
        _next = form.cleaned_data.get('next')
        if not devise:
            raise Http404()
        if self.request.user.is_authenticated:
            prefs = UserPreference.objects.get_or_create(user=self.request.user)
            prefs = prefs[0]
            prefs.devise = devise
            prefs.save()
        request.session['user_devise'] = devise.name
        if _next:
            return redirect(_next)
        return redirect(reverse('index'))

class NewsLetterSubscriptionView(LoginRequiredMixin, PostView):

    def get(self, request, *args, **kwargs):
        return redirect(reverse('index'))

    def post(self, request, *args, **kwargs):
        form = NewsLetterSubscription(request.POST)
        if not form.is_valid():
            raise Http404()
        user_subscription = MailSubscription.objects.filter(user=request.user).first()
        if not user_subscription:
            subscription = MailSubscription()
            subscription.user = request.user
            subscription.save()
            messages.success(request, _('Your subscription is activated successfully.'))

        return HttpResponseRedirect(reverse('index'))

