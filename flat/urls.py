from django.urls import path
from .views import (
    AddFlatView,
    OwnerFlatListView,
    OwnerFlatUpdateDeleteView,
    FlatDetailView,
    FlatListView,
    SendMessageView,
    RenterBookingListView,
    RenterBookingDeleteView
)

urlpatterns = [
    path('owner/flats/add/', AddFlatView.as_view(), name='add-flat'),
    path('owner/flats_list/', OwnerFlatListView.as_view(), name='list-owner-flats'),
    path('owner/flats/<int:flat_id>/', OwnerFlatUpdateDeleteView.as_view(), name='update-delete-flat'),
    path('renter/bookings/', RenterBookingListView.as_view(), name='renter-bookings'),
    path('renter/bookings/delete/<slug:slug>/', RenterBookingDeleteView.as_view(), name='delete-booking'),
    path('all_flats/', FlatListView.as_view(), name='list-flats'),
    path('flat_details/<str:slug>/', FlatDetailView.as_view(), name='flta-details'),
    path('send_message/<slug:slug>/', SendMessageView.as_view(), name='send-message'),
]
