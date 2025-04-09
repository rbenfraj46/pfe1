from django.urls import path
from home.views.car import CarModelDetailsView

urlpatterns = [
    path('model/<int:pk>/', CarModelDetailsView.as_view(), name='car_model_details'),
]
