#!/usr/bin/python
from django.urls import path
from django.urls import re_path
from django.contrib.auth import views as auth_views
from djgeojson.views import GeoJSONLayerView
from django.views.generic import TemplateView 
from home.views import index, ajax_views
from home.views import connection_views
from home.views import registration
from home.views import agences
from home.views import contact
from home.views import ajax_views
from home.views.agences import CarModelsJsonView
from home.views.agences import activate_agency
from home.views.agences import MailNotConfirmedAgencyView
from home.views.agences import AgencyCarsListView
from home.views.agences import UpdateCarView
from home.views.agences import DeleteCarView
from .views.car import update_car
from home.views.car import CarModelRequestView
from home.views.car import CarModelRequestHistoryView
from home.views.car import CarSearchView
from home.views.car import CarSearchResultsView
from home.views.car import CarSearchFilterView
from home.views.car import CarRentalRequestView

from home.models import State

urlpatterns = [
    re_path(r'^$', index.IndexView.as_view(), name='index'),
    re_path(r'^index.php$', index.IndexView.as_view(), name='index'),
    re_path(r'^setDevice.php$', index.DeviseView.as_view(), name='set_devise'),
    re_path(r'^login.php$', connection_views.login_view.as_view(), name='login'),
    re_path(r'^forgetpassword.php$', connection_views.ForgetPassword.as_view(), name='sendPassword'),
    re_path(r'^mailNotConfirmed.php$', connection_views.MailNotConfirmedView.as_view(), name='mail_not_confirmed'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', connection_views.ResetDoneView.as_view(), name='password_reset_complete'),
    path('reset/done/', connection_views.ResetDoneView.as_view(), name='password_change_done'),
    path('changepassword.php', connection_views.ChangePasswordView.as_view(),name='password_change'),
    path('logout.php', auth_views.LogoutView.as_view(), name='logout'),
    re_path(r'^registration.php$', registration.RegisterationView.as_view(), name='registration'),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$',
        registration.activate, name='activate'),
    path('contact.php', contact.ContactView.as_view(),name='contact'),
    path('newsletter.php', index.NewsLetterSubscriptionView.as_view(),name='newsletter'),
    re_path(r'^agence.php$', agences.AgencesView.as_view(), name='agences'),
    re_path(r'^agences/create$', agences.RegisterView.as_view(), name='agences_register'),
    re_path(r'^data.geojson$', GeoJSONLayerView.as_view(model=State, properties=['name']), name='data'),
    re_path(r'^delegations$', ajax_views.DelegationsJsonView.as_view(), name='delegations'),
    re_path(r'^cities$', ajax_views.CitiesJsonView.as_view(), name='cities'),
    path('agences/manage/<int:agency_id>/', agences.ManageAgenceView.as_view(), name='manage_agence'),
    path('agences/pending/', agences.PendingAgenceView.as_view(), name='pending_agence'),
    path('agences/user/', agences.UserAgenciesView.as_view(), name='user_agencies'),
    path('agences/car/add/<int:agency_id>/', agences.RegisterCarView.as_view(), name='car_add'),
    path('car-models-json/', CarModelsJsonView.as_view(), name='car_models_json'),
    path('activate_agency/<uidb64>/<token>/', activate_agency, name='activate_agency'),
    path('mailNotConfirmedAgency.php', MailNotConfirmedAgencyView.as_view(), name='mail_not_confirmed_agency'),
    path('agency-cars/<int:agency_id>/', AgencyCarsListView.as_view(), name='agency_cars_list'),
    path('agences/car/update/<int:pk>/', UpdateCarView.as_view(), name='car_update'),
    path('agences/car/delete/<int:pk>/', DeleteCarView.as_view(), name='car_delete'),
    path('car/update/<int:car_id>/', update_car, name='car_update'),
    path('car-model/request/', CarModelRequestView.as_view(), name='request_car_model'),
    path('car-model/requests/history/', CarModelRequestHistoryView.as_view(), name='car_model_requests_history'),
    path('terms-and-conditions/', TemplateView.as_view(template_name="terms_and_conditions.html"), name='terms_and_conditions'),
    path('cars/<int:car_id>/rent/', CarRentalRequestView.as_view(), name='rental_request'),
    path('cars/search/', CarSearchView.as_view(), name='car_search'),
    path('cars/search/results/', CarSearchResultsView.as_view(), name='car_search_results'),
    path('cars/search/filter/', CarSearchFilterView.as_view(), name='car_search_filter'),
]
