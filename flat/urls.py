from django.urls import path
from .views import (
    AddFlatView,
    FlatListView,
    FlatUpdateDeleteView
)

urlpatterns = [
    path('flats/add/', AddFlatView.as_view(), name='add-flat'),
    path('flats/', FlatListView.as_view(), name='list-flats'),
    path('flats/<int:flat_id>/', FlatUpdateDeleteView.as_view(), name='update-delete-flat'),
]
