import logging
import json

from django.http import JsonResponse
from django.views.generic import TemplateView
from django.http.response import HttpResponseNotFound
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers.json import DjangoJSONEncoder

from django.contrib.gis.geos import Point

from django.conf import settings

from home.models import Delegation
from home.models import City


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
