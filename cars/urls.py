from django.urls import path
from home.views.car import CarModelDetailsView
from .views.rental import RentalStatusUpdateView, AgencyRentalsView

urlpatterns = [
    path('model/<int:pk>/', CarModelDetailsView.as_view(), name='car_model_details'),
    path('agency/<int:agency_id>/rentals/', AgencyRentalsView.as_view(), name='agency_rentals'),
    path('rentals/<int:reservation_id>/update-status/', RentalStatusUpdateView.as_view(), name='update_rental_status'),
]
