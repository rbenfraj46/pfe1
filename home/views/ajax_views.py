import logging
import json

from django.http import JsonResponse
from django.views.generic import TemplateView, View
from django.http.response import HttpResponseNotFound
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers.json import DjangoJSONEncoder

from django.contrib.gis.geos import Point

from django.conf import settings

from home.models import Delegation
from home.models import City
from home.models import Agences
from cars.models import CarReservation, CarModelRequest  # Modifié: import depuis cars.models


logger = logging.getLogger(__file__)

class GeoJsonEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, Point):
            # convert get coordinate as tuple (lat, long)
            return o.coords
        # if isinstance(o, datetime.datetime):
        #     # return something like /Date(211870800000)/ for gijgo
        #     ##  Saturday, September 18, 1976 6:00:00 AM GMT+01:00
        #     time_stamp = int(o.timestamp()) * 1000
        #     timestamp = time_stamp + DAYLIGHT_PREFIX
        #     return "/Date(%s)/" % time_stamp
        return DjangoJSONEncoder.default(self, o)


class JSONResponseMixin:
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        result = {}
        try:
            data = self.get_data(context)
            result['status_code'] = 200
            result['data'] = data
        except Exception as exp:
            logger.error("Exception occured: %s", exp)
            result['status_code'] = 500
            result['data'] = "Internal Server Error"

        return JsonResponse(
            result,
            encoder=GeoJsonEncoder,
            **response_kwargs
        )

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return context


class JSONView(LoginRequiredMixin, JSONResponseMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            return super().get(self, request, *args, **kwargs)
        else:
            if settings.DEBUG:
                return super().get(self, request, *args, **kwargs)
            return HttpResponseNotFound()

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)


class DelegationsJsonView(JSONView):

    def get_context_data(self, **kwargs):
        context = {}
        state = self.request.GET.get('state', '')
        delegations = []
        if state:
            delegations = list(Delegation.objects.filter(state__id=state).values('id', 'name'))
        context['delegations'] = delegations
        return context


class CitiesJsonView(JSONView):

    def get_context_data(self, **kwargs):
        context = {}
        state = self.request.GET.get('delegation', '')
        cities = []
        if state:
            cities = list(City.objects.filter(delegation__id=state).values('id', 'name', 'zipcode', 'position'))
        context['cities'] = cities # json.dumps(cities, cls=GeoJsonEncoder)
        return context


class AdminNotificationsView(View):
    def get(self, request):
        if not request.user.is_staff:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
            
        # Récupérer les notifications non lues
        notifications = {
            'rental': CarReservation.objects.filter(status='pending').count(),
            'car_model': CarModelRequest.objects.filter(status='pending').count(),
            'agency': Agences.objects.filter(is_active=False, is_mail_verified=True).count()
        }
        
        # Calculer le total
        total_count = sum(notifications.values())
        
        # Préparer les détails des notifications
        notification_details = []
        
        # Demandes de location en attente
        for reservation in CarReservation.objects.filter(status='pending')[:5]:
            notification_details.append({
                'type': 'rental',
                'message': f'New rental request for {reservation.car}',
                'url': f'/admin/cars/carreservation/{reservation.id}/change/',
                'time': reservation.created_at.strftime('%Y-%m-%d %H:%M')
            })
            
        # Demandes de modèles de voiture
        for request in CarModelRequest.objects.filter(status='pending')[:5]:
            notification_details.append({
                'type': 'car_model',
                'message': f'New car model request: {request.brand_name} {request.model_name}',
                'url': f'/admin/cars/carmodelrequest/{request.id}/change/',
                'time': request.created_at.strftime('%Y-%m-%d %H:%M')
            })
            
        # Agences en attente d'activation
        for agency in Agences.objects.filter(is_active=False, is_mail_verified=True)[:5]:
            notification_details.append({
                'type': 'agency',
                'message': f'New agency registration: {agency.agency_name}',
                'url': f'/admin/home/agences/{agency.id}/change/',
                'time': agency.creation_date.strftime('%Y-%m-%d %H:%M')
            })
            
        return JsonResponse({
            'count': total_count,
            'notifications': sorted(notification_details, key=lambda x: x['time'], reverse=True)
        })
