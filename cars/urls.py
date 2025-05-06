from django.urls import path
from .views.rental import RentalStatusUpdateView, AgencyRentalsView
from .views.car import (
    CarManagementMixin,
    CarRentalRequestView,
    CarModelRequestView,
    CarModelRequestHistoryView,
    UpdateCarView,
    DeleteCarView,
    AgencyCarListView,
    RegisterCarView,
    CarModelsJsonView,
    CarModelDetailsView,
    UserReservationsView,
    CancelReservationView,
    CarDetailView,
    CalculateRentalTotalView
)
from .views.search import (
    CarSearchView,
    CarSearchResultsView,
    CarSearchFilterView,
    CarSearchDebugView
)
# Import des vues de transfert
from .views.transfer import (
    TransferVehicleListView,
    TransferVehicleCreateView,
    TransferBookingListView,
    TransferSearchView,
    TransferSearchResultsView,
    TransferBookingView
)

urlpatterns = [
    # Vues détaillées
    path('detail/<int:pk>/', CarDetailView.as_view(), name='car_detail'),
    path('model/<int:pk>/', CarModelDetailsView.as_view(), name='car_model_details'),
    
    # Gestion des locations
    path('agency/<int:agency_id>/rentals/', AgencyRentalsView.as_view(), name='agency_rentals'),
    path('rentals/<int:reservation_id>/update-status/', RentalStatusUpdateView.as_view(), name='update_rental_status'),
    
    # Gestion des voitures d'agence
    path('agency/cars/<int:agency_id>/', AgencyCarListView.as_view(), name='agency_cars_list'),
    path('agency/car/add/<int:agency_id>/', RegisterCarView.as_view(), name='car_add'),
    path('agency/car/update/<int:pk>/', UpdateCarView.as_view(), name='car_update'),
    path('agency/car/delete/<int:pk>/', DeleteCarView.as_view(), name='car_delete'),
    
    # API et modèles de voiture
    path('car-models/', CarModelsJsonView.as_view(), name='car_models_json'),
    path('car-model/request/', CarModelRequestView.as_view(), name='request_car_model'),
    path('car-model/requests/history/', CarModelRequestHistoryView.as_view(), name='car_model_requests_history'),
    
    # Recherche de voitures
    path('search/', CarSearchView.as_view(), name='car_search'),
    path('search/results/', CarSearchResultsView.as_view(), name='car_search_results'),
    path('search/filter/', CarSearchFilterView.as_view(), name='car_search_filter'),
    path('search/debug/', CarSearchDebugView.as_view(), name='car_search_debug'),
    
    # Gestion des réservations
    path('rent/<int:car_id>/', CarRentalRequestView.as_view(), name='rental_request'),
    path('my-reservations/', UserReservationsView.as_view(), name='user_reservations'),
    path('reservations/<int:reservation_id>/cancel/', CancelReservationView.as_view(), name='cancel_reservation'),
    
    # Calcul du total de location
    path('api/calculate-rental-total/', CalculateRentalTotalView.as_view(), name='calculate_rental_total'),
    
    # URLs pour la gestion des transferts
    path('transfers/agency/<int:agency_id>/vehicles/', TransferVehicleListView.as_view(), name='agency_transfer_vehicles'),
    path('transfers/agency/<int:agency_id>/vehicles/add/', TransferVehicleCreateView.as_view(), name='add_transfer_vehicle'),
    path('transfers/search/', TransferSearchView.as_view(), name='transfer_search'),
    path('transfers/search/results/', TransferSearchResultsView.as_view(), name='transfer_search_results'),
    path('transfers/book/<int:vehicle_id>/', TransferBookingView.as_view(), name='transfer_booking'),
    path('transfers/my-bookings/', TransferBookingListView.as_view(), name='my_transfer_bookings'),
]
