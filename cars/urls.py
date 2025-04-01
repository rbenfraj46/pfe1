from django.urls import path
from home.views.car import CarModelDetailsView

urlpatterns = [
    # ...existing urls...
    path('model-details/', CarModelDetailsView.as_view(), name='car_model_details'),
]
