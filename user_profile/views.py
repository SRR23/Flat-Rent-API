
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import User
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail
import jwt
import datetime
# Create your views here.
from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
)


class RegistrationView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False  # Deactivate the user until email confirmation
            user.save()

            # Generate activation token
            expiration_time = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24)
            token = jwt.encode(
                {"user_id": user.id, "exp": expiration_time},
                settings.SECRET_KEY,
                algorithm="HS256"
            )

            # Generate activation URL dynamically
            activation_url = request.build_absolute_uri(reverse('activate-account', args=[token]))

            # Send activation email
            send_mail(
                subject="Activate Your Account",
                message=f"Click the link to activate your account: {activation_url}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )

            return Response(
                {"status": "success", "message": "User registered. Check your email to activate your account."},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ActivateAccountView(APIView):
    def get(self, request, token):
        try:
            # Decode the token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])
            
            if user.is_active:
                return Response(
                    {"status": "error", "message": "Account already activated."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Activate the user account
            user.is_active = True
            user.save()
            
            return Response(
                {"status": "success", "message": "Account activated successfully. You can now log in."},
                status=status.HTTP_200_OK
            )

        except jwt.ExpiredSignatureError:
            return Response({"status": "error", "message": "Activation link expired."}, status=status.HTTP_400_BAD_REQUEST)

        except jwt.DecodeError:
            return Response({"status": "error", "message": "Invalid activation token."}, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, email=email, password=password)

        if user:
            if not user.is_active:
                return Response(
                    {"status": "error", "message": "Account is not activated. Check your email."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "status": "success",
                    "user": {"email": user.email, "user_type": user.user_type},
                    "token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"status": "unauthorized", "message": "Invalid email or password"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def perform_update(self, serializer):
        serializer.save()  # No need to pass user here since the serializer handles it