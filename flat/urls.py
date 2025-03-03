from django.urls import path
from .views import (
    AddFlatView,
    OwnerFlatListView,
    FlatUpdateDeleteView,
    FlatDetailView,
    FlatListView,
    SendMessageView
)

urlpatterns = [
    path('flats/add/', AddFlatView.as_view(), name='add-flat'),
    path('flats/', OwnerFlatListView.as_view(), name='list-owner-flats'),
    path('flats/<int:flat_id>/', FlatUpdateDeleteView.as_view(), name='update-delete-flat'),
    path('all_flats/', FlatListView.as_view(), name='list-flats'),
    path('flat_details/<str:slug>/', FlatDetailView.as_view(), name='flta-details'),
    path('send_message/<slug:slug>/', SendMessageView.as_view(), name='send-message'),
]
