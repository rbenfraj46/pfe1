from django.urls import path
from .views.rental import RentalStatusUpdateView, AgencyRentalsView
from .views.car import (
    CarManagementMixin,
    CarRentalRequestView,
    CarModelRequestView,
    CarModelRequestHistoryView,
    UpdateCarView,
    DeleteCarView,
    AgencyCarsListView,
    RegisterCarView,
    CarModelsJsonView,
    CarModelDetailsView,
    UserReservationsView,
    CancelReservationView
)
from .views.search import (
    CarSearchView,
    CarSearchResultsView,
    CarSearchFilterView,
    CarSearchDebugView
)

urlpatterns = [
    path('model/<int:pk>/', CarModelDetailsView.as_view(), name='car_model_details'),
    path('agency/<int:agency_id>/rentals/', AgencyRentalsView.as_view(), name='agency_rentals'),
    path('rentals/<int:reservation_id>/update-status/', RentalStatusUpdateView.as_view(), name='update_rental_status'),
    path('agency/cars/<int:agency_id>/', AgencyCarsListView.as_view(), name='agency_cars_list'),
    path('agency/car/add/<int:agency_id>/', RegisterCarView.as_view(), name='car_add'),
    path('agency/car/update/<int:pk>/', UpdateCarView.as_view(), name='car_update'),
    path('agency/car/delete/<int:pk>/', DeleteCarView.as_view(), name='car_delete'),
    path('car-models/', CarModelsJsonView.as_view(), name='car_models_json'),
    path('car-model/request/', CarModelRequestView.as_view(), name='request_car_model'),
    path('car-model/requests/history/', CarModelRequestHistoryView.as_view(), name='car_model_requests_history'),
    path('cars/search/', CarSearchView.as_view(), name='car_search'),
    path('cars/search/results/', CarSearchResultsView.as_view(), name='car_search_results'),
    path('cars/search/filter/', CarSearchFilterView.as_view(), name='car_search_filter'),
    path('cars/search/debug/', CarSearchDebugView.as_view(), name='car_search_debug'),
    path('cars/rent/<int:car_id>/', CarRentalRequestView.as_view(), name='rental_request'),
    path('my-reservations/', UserReservationsView.as_view(), name='user_reservations'),
    path('reservations/<int:reservation_id>/cancel/', CancelReservationView.as_view(), name='cancel_reservation'),
]
