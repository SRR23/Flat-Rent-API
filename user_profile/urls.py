from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views
from .views import (
    RegistrationView,
    ActivateAccountView,
    LoginView,
    UserProfileViewSet,
)

router = DefaultRouter()
router.register(r'profile', UserProfileViewSet, basename='user-profile')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegistrationView.as_view(), name = 'register'),
    path('activate/<str:token>/', ActivateAccountView.as_view(), name='activate-account'),
    path('login/', LoginView.as_view(), name = 'login'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]