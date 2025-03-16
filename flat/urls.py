
from django.urls import path
from .views import (
    AddFlatView,
    OwnerFlatListView,
    OwnerFlatUpdateDeleteView,
    FlatDetailView,
    FlatListView,
    SendMessageView,
    RenterBookingListView,
    RenterBookingDeleteView,
    FlatCategoryFilterView,
    FlatSearchView,
    CategoryListView,
    LocationListView,
    HomeView,
)

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('owner/flats/add/', AddFlatView.as_view(), name='add-flat'),
    path('owner/flats_list/', OwnerFlatListView.as_view(), name='list-owner-flats'),
    path('owner/flats/<int:flat_id>/', OwnerFlatUpdateDeleteView.as_view(), name='update-delete-flat'),
    path('renter/bookings/', RenterBookingListView.as_view(), name='renter-bookings'),
    path('renter/bookings/delete/<slug:slug>/', RenterBookingDeleteView.as_view(), name='delete-booking'),
    path('renter/send_message/<slug:slug>/', SendMessageView.as_view(), name='send-message'),
    path('all_flats/', FlatListView.as_view(), name='list-flats'),
    path('flat_details/<str:slug>/', FlatDetailView.as_view(), name='flat-details'),
    path('filter_category/', FlatCategoryFilterView.as_view(), name='category'),
    path('search/', FlatSearchView.as_view(), name='search'),
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('locations/', LocationListView.as_view(), name='locations'),
]
