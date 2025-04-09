from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls.base import reverse
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from django.views import View
from django.http import JsonResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from home.forms.agences_forms import AgencesForm
from home.models import (
    State,
    RightsAccess,
    RIGHTS_TYPE,
    RIGHTS_NAME,
    Agences,
    AgencyPermission,
    User
)
from home.views.index import IndexView
from cars.models import Brand, CarModel
from home.tokens import account_activation_token
from home.mail_util import send_mail_verification_agency

def has_agence(user):
    if RightsAccess.objects.filter(user=user, name=RIGHTS_NAME['agence']).first():
        return True
    return False

def has_agency_permission(user, agency_id, permission):
    return AgencyPermission.objects.filter(
        user=user,
        agency_id=agency_id,
        permission=permission
    ).exists()

class AgencesView(LoginRequiredMixin, IndexView):
    template_name = "agences_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        if not has_agence(request.user):
            return redirect(reverse('agences_register'))
        return super().get(self, request, *args, **kwargs)

class RegisterView(LoginRequiredMixin, IndexView):
    template_name = "agences/create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lat'] = settings.DEFAULT_LAT
        context['lon'] = settings.DEFAULT_LON
        context['states'] = State.objects.values('id', 'name').order_by('order_key')
        return context

    def post(self, request, *args, **kwargs):
        form = AgencesForm(request.POST, request.FILES)
        if form.is_valid():
            agence = form.save(commit=False)
            agence.creator = self.request.user
            agence.logo = request.FILES.get('logo')
            agence.save()
            send_mail_verification_agency(request, agence)
            messages.success(request, _('Agence created Successfully. Please check your mail box and hit the mail verification.'))
            return redirect(reverse('index'))
        else:
            return render(request, 'agences/create.html', {'form_reg': form, 'action_name': _('Register')}, status=200)

class ManageAgenceView(LoginRequiredMixin, TemplateView):
    template_name = 'agences/manage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agency_id = self.kwargs.get('agency_id')
        agence = get_object_or_404(self.request.user.agences_set, id=agency_id, is_active=True)
        context['agence'] = agence
        return context

class PendingAgenceView(LoginRequiredMixin, TemplateView):
    template_name = 'agences/pending.html'

class UserAgenciesView(LoginRequiredMixin, TemplateView):
    template_name = 'agences/user_agencies.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['user_owned_agencies'] = self.request.user.agences_set.all()
        
        user_permissions = AgencyPermission.objects.filter(
            user=self.request.user
        ).select_related('agency').order_by('agency_id')
        
        permission_groups = {}
        for perm in user_permissions:
            if perm.agency_id not in permission_groups:
                permission_groups[perm.agency_id] = {
                    'agency': perm.agency,
                    'permissions': []
                }
            permission_groups[perm.agency_id]['permissions'].append(perm)
        
        context['user_permissions'] = permission_groups.values()
        return context

class MailNotConfirmedAgencyView(LoginRequiredMixin, TemplateView):
    template_name = 'mail_not_confirmed_agency.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_rq'] = self.request.user
        return context

    def post(self, request, *args, **kwargs):
        send_mail_verification_agency(request, request.user)
        messages.success(request, _("Activation email has been resent."))
        return redirect('mail_not_confirmed_agency')

def activate_agency(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        agence = Agences.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Agences.DoesNotExist):
        agence = None

    if agence is not None and account_activation_token.check_token(agence, token):
        agence.is_mail_verified = True
        agence.save()
        messages.success(request, _('Your agency mail address is successfully activated.'))
        return redirect(reverse('index'))
    else:
        messages.error(request, _('This link is invalid. Try to generate another link.'))
        return redirect(reverse('index'))

class AgencyPermissionView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'agences/permissions.html'

    def test_func(self):
        agency_id = self.kwargs.get('agency_id')
        return Agences.objects.filter(id=agency_id, creator=self.request.user).exists()

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)
        raise PermissionDenied

    def get(self, request, agency_id):
        try:
            agency = get_object_or_404(Agences, id=agency_id)
            permissions = AgencyPermission.objects.select_related('user', 'granted_by').filter(agency=agency)
            context = {
                'agency': agency,
                'permissions': permissions,
                'permission_choices': AgencyPermission.PERMISSION_CHOICES
            }
            return render(request, self.template_name, context)
        except Exception as e:
            messages.error(request, str(e))
            return redirect('manage_agence', agency_id=agency_id)

    def post(self, request, agency_id):
        agency = get_object_or_404(Agences, id=agency_id)
        email = request.POST.get('user_email')
        permissions = request.POST.getlist('permissions')
        
        try:
            user = User.objects.get(email=email)
            
            AgencyPermission.objects.filter(agency=agency, user=user).delete()
            
            for perm in permissions:
                AgencyPermission.objects.create(
                    agency=agency,
                    user=user,
                    permission=perm,
                    granted_by=request.user
                )
            
            messages.success(request, _('Permissions updated successfully'))
        except User.DoesNotExist:
            messages.error(request, _('User not found'))
        
        return redirect('agency_permissions', agency_id=agency_id)

class RevokeAgencyPermissionView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        agency_id = self.kwargs.get('agency_id')
        return Agences.objects.filter(id=agency_id, creator=self.request.user).exists()

    def post(self, request, agency_id, permission_id):
        try:
            permission = get_object_or_404(AgencyPermission, 
                id=permission_id, 
                agency_id=agency_id
            )
            user_email = permission.user.email
            permission.delete()
            messages.success(request, _('Permission revoked successfully from {}').format(user_email))
        except Exception as e:
            messages.error(request, _('Error revoking permission: {}').format(str(e)))
        
        return redirect('agency_permissions', agency_id=agency_id)

class CarModelsJsonView(View):
    def get(self, request, *args, **kwargs):
        brand_id = request.GET.get('brand_id')
        models_qs = CarModel.objects.filter(brand_id=brand_id)
        data = [{'id': m.id, 'name': m.name} for m in models_qs]
        return JsonResponse(data, safe=False)
