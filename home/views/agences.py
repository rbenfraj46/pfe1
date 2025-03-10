from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.urls.base import reverse
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from home.forms.agences_forms import AgencesForm

from home.models import State
from home.models import RightsAccess
from home.models import RIGHTS_TYPE, RIGHTS_NAME

from home.views.index import IndexView

def has_agence(user):
    if RightsAccess.objects.filter(user=user, name=RIGHTS_NAME['agence']).first():
        return True
    return False

# Create your views here.
class AgencesView(LoginRequiredMixin, IndexView):
    template_name =  "agences_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        if not has_agence(request.user):
            return redirect(reverse('agences_register'))
        return super().get(self, request, *args, **kwargs)

class RegisterView(LoginRequiredMixin, IndexView):
    template_name =  "agences/create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lat'] = settings.DEFAULT_LAT
        context['lon'] = settings.DEFAULT_LON
        context['states'] = State.objects.values('id', 'name').order_by('order_key')
        return context

    def post(self, request, *args, **kwargs):
        form = AgencesForm(request.POST)
        if form.is_valid():
            agence = form.save(commit=False)
            agence.creator = self.request.user
            agence.save()
            messages.success(request, _('Agence created Successfully. Please check your mail box and hit the mail verification.'))
            return redirect(reverse('index'))
        else:
            return render(request, 'agences/create.html', {'form_reg': form, 'action_name': _('Register')}, status=200)

class ManageAgenceView(LoginRequiredMixin, TemplateView):
    template_name = 'agences/manage.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.agences_set.filter(is_active=True).exists():
            return redirect('pending_agence')
        return super().dispatch(request, *args, **kwargs)

class PendingAgenceView(LoginRequiredMixin, TemplateView):
    template_name = 'agences/pending.html'
