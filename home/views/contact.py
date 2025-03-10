from django.shortcuts import render, redirect
from django.urls.base import reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.gis import forms as gisForm

from home.views.index import IndexView

from home.forms.contact_forms import ContactForm
from django.conf import settings


class MyLocation(gisForm.Form):
    point = gisForm.PointField(widget=
        gisForm.OSMWidget(attrs={'map_width': '100%', 'map_height': 500,
                                 'default_lon':'10.3124463',
                                 'default_lat':'36.8325412',
                                 'default_zoom': 16,
                                 }))


class ContactView(IndexView):
    template_name =  "contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['location'] = MyLocation()
        context['lat'] = settings.DEFAULT_LAT
        context['lon'] = settings.DEFAULT_LON
        return context

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if not form.is_valid():
            return render(request, 'contact.html', {'form': form})

        contact = form.save(commit=False)
        if self.request.user.is_authenticated:
            contact.user = self.request.user
        contact.save()
        messages.success(request, _('Thank you for contacting us. We will reply you As Soon As Possible'))
        return redirect(reverse('index'))
