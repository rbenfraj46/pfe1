#!/usr/bin/python
from django.urls import path
from django.urls import re_path
from django.contrib.auth import views as auth_views
from djgeojson.views import GeoJSONLayerView
from django.views.generic import TemplateView 

from home.views import (
    index,
    ajax_views,
    connection_views,
    registration,
    agences,
    contact
)

from home.models import State

urlpatterns = [
    # Pages générales
    path('', index.IndexView.as_view(), name='index'),
    path('index.php', index.IndexView.as_view(), name='index'),
    path('setDevice.php', index.DeviseView.as_view(), name='set_devise'),
    path('contact.php', contact.ContactView.as_view(), name='contact'),
    path('newsletter.php', index.NewsLetterSubscriptionView.as_view(), name='newsletter'),
    
    # Authentification et gestion du compte
    path('login.php', connection_views.login_view.as_view(), name='login'),
    path('forgetpassword.php', connection_views.ForgetPassword.as_view(), name='sendPassword'),
    path('mailNotConfirmed.php', connection_views.MailNotConfirmedView.as_view(), name='mail_not_confirmed'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', connection_views.ResetDoneView.as_view(), name='password_reset_complete'),
    path('reset/done/', connection_views.ResetDoneView.as_view(), name='password_change_done'),
    path('changepassword.php', connection_views.ChangePasswordView.as_view(), name='password_change'),
    path('logout.php', auth_views.LogoutView.as_view(), name='logout'),
    
    # Inscription et activation
    path('registration.php', registration.RegisterationView.as_view(), name='registration'),
    path('activate/<uidb64>/<token>/', registration.activate, name='activate'),
    
    # Gestion des agences
    path('agence.php', agences.AgencesView.as_view(), name='agences'),
    path('agences/create', agences.RegisterView.as_view(), name='agences_register'),
    path('agences/manage/<int:agency_id>/', agences.ManageAgenceView.as_view(), name='manage_agence'),
    path('agences/pending/', agences.PendingAgenceView.as_view(), name='pending_agence'),
    path('agences/user/', agences.UserAgenciesView.as_view(), name='user_agencies'),
    path('agences/<int:agency_id>/permissions/', agences.AgencyPermissionView.as_view(), name='agency_permissions'),
    path('activate_agency/<uidb64>/<token>/', agences.activate_agency, name='activate_agency'),
    path('mailNotConfirmedAgency.php', agences.MailNotConfirmedAgencyView.as_view(), name='mail_not_confirmed_agency'),
    path('agency/<int:agency_id>/permissions/<int:permission_id>/revoke/', 
        agences.RevokeAgencyPermissionView.as_view(), 
        name='revoke_agency_permission'),
    path('agency/<int:agency_id>/update-settings/', agences.AgencySettingsUpdateView.as_view(), name='agency_settings_update'),
    
    # Données géographiques
    path('data.geojson', GeoJSONLayerView.as_view(model=State, properties=['name']), name='data'),
    path('delegations', ajax_views.DelegationsJsonView.as_view(), name='delegations'),
    path('cities', ajax_views.CitiesJsonView.as_view(), name='cities'),
    
    # Pages statiques
    path('terms-and-conditions/', TemplateView.as_view(template_name="terms_and_conditions.html"), name='terms_and_conditions'),
]
