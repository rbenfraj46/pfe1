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

from home.forms.agences_forms import AgencesForm

from home.models import State
from home.models import RightsAccess
from home.models import RIGHTS_TYPE, RIGHTS_NAME
from home.models import Agences

from home.views.index import IndexView
from cars.models import AgencyCar, Brand, CarModel, GearType  # import des modèles de voitures
from home.tokens import account_activation_token
from home.mail_util import send_mail_verification_agency

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
        form = AgencesForm(request.POST ,request.FILES)
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
        
        # Retrieve the agency of the logged-in user
        agence = self.request.user.agences_set.filter(is_active=True).first()
        
        if not agence:
            return redirect('pending_agence')  

        context['agence'] = agence 
        return context


class PendingAgenceView(LoginRequiredMixin, TemplateView):
    template_name = 'agences/pending.html'

class UserAgenciesView(LoginRequiredMixin, TemplateView):
    template_name = 'agences/user_agencies.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['agencies'] = self.request.user.agences_set.all()
        return context

class RegisterCarView(View):
    template_name = "agences/car_form.html"

    def get(self, request, *args, **kwargs):
        context = {
            'brands': Brand.objects.filter(is_active=True),
            'car_models': [],  # Initial empty list for car models
            'gear_types': GearType.objects.filter(is_active=True),  # Add gear_types to context
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Récupérer les données du formulaire
        brand_id = request.POST.get('brand')
        model_id = request.POST.get('car_model')
        fuel_policy = request.POST.get('fuel_policy')
        security_deposit = request.POST.get('security_deposit')
        minimum_license_age = request.POST.get('minimum_license_age')
        price_per_day = request.POST.get('price_per_day')
        available = request.POST.get('available') == 'on'
        image = request.FILES.get('image')
        gear_type_id = request.POST.get('gear_type')

        agency_car = AgencyCar()
        agency_car.agence = request.user.agences_set.filter(is_active=True).first()
        agency_car.brand = Brand.objects.filter(id=brand_id).first()
        agency_car.car_model = CarModel.objects.filter(id=model_id).first()
        agency_car.fuel_policy = fuel_policy
        agency_car.security_deposit = security_deposit
        agency_car.minimum_license_age = minimum_license_age
        agency_car.price_per_day = price_per_day
        agency_car.is_active = False  # Affectation automatique à False
        agency_car.available = available
        agency_car.gear_type = GearType.objects.filter(id=gear_type_id).first()
        if image:
            agency_car.image = image

        agency_car.save()
        return redirect('agency_cars_list')

class UpdateCarView(View):
    template_name = "agences/update_car_form.html"

    def get(self, request, *args, **kwargs):
        car_id = kwargs.get('pk')
        car = get_object_or_404(AgencyCar, pk=car_id)
        context = {
            'car': car,
            'brands': Brand.objects.filter(is_active=True),
            'car_models': CarModel.objects.filter(brand=car.brand),
            'gear_types': GearType.objects.filter(is_active=True),
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        car_id = kwargs.get('pk')
        car = get_object_or_404(AgencyCar, pk=car_id)
        car.brand_id = request.POST.get('brand')
        car.car_model_id = request.POST.get('car_model')
        car.fuel_policy = request.POST.get('fuel_policy')
        car.security_deposit = request.POST.get('security_deposit')
        car.minimum_license_age = request.POST.get('minimum_license_age')
        car.price_per_day = request.POST.get('price_per_day')
        car.available = request.POST.get('available') == 'on'
        car.gear_type_id = request.POST.get('gear_type')
        if request.FILES.get('image'):
            car.image = request.FILES.get('image')
        car.save()
        return redirect('agency_cars_list')

class CarModelsJsonView(View):
    def get(self, request, *args, **kwargs):
        brand_id = request.GET.get('brand_id')
        models_qs = CarModel.objects.filter(brand_id=brand_id)
        data = [{'id': m.id, 'name': m.name} for m in models_qs]
        return JsonResponse(data, safe=False)

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

class DeleteCarView(View):
    def post(self, request, *args, **kwargs):
        car_id = kwargs.get('pk')
        car = get_object_or_404(AgencyCar, pk=car_id)
        car.is_active = False
        car.save()
        return JsonResponse({'success': True})

class AgencyCarsListView(LoginRequiredMixin, ListView):
    template_name = 'agences/agency_cars_list.html'
    context_object_name = 'agency_cars'
    paginate_by = 10

    def get_queryset(self):
        queryset = AgencyCar.objects.filter(agence__creator=self.request.user, is_active=True)
        brand = self.request.GET.get('brand')
        gear_type = self.request.GET.get('gear_type')
        if brand:
            queryset = queryset.filter(brand__name__icontains=brand)
        if gear_type:
            queryset = queryset.filter(gear_type__name__icontains=gear_type)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_car_url'] = reverse_lazy('register_car')
        context['brands'] = Brand.objects.filter(is_active=True)
        context['gear_types'] = GearType.objects.filter(is_active=True)
        return context
