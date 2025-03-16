
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import User
from django.conf import settings
from django.urls import reverse
# from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import HttpResponseRedirect
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
            user_data = serializer.validated_data
            user_data.pop('confirm_password')  # ✅ Remove confirm_password for all users

            # ✅ Ensure required owner fields are stored properly
            if user_data['user_type'] == 'owner':
                user = User.objects.create_user(
                    user_type=user_data['user_type'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    email=user_data['email'],
                    phone_number=user_data['phone_number'],
                    password=user_data['password'],
                    house_holding_number=user_data.get('house_holding_number', ''),
                    address=user_data.get('address', '')
                )
            else:
                user = User.objects.create_user(**user_data)  # ✅ Now confirm_password is removed

            user.is_active = False  # Deactivate until email confirmation
            user.save()

            # 🔐 Generate activation token (expires in 24 hours)
            expiration_time = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24)
            token = jwt.encode(
                {"user_id": user.id, "exp": expiration_time},
                settings.SECRET_KEY,
                algorithm="HS256"
            )

            # 📩 Generate activation URL dynamically
            activation_url = request.build_absolute_uri(reverse('activate-account', args=[token]))

            # 📧 Load email template
            email_html_message = render_to_string(
                'emails/activation_email.html',
                {'activation_url': activation_url}
            )
            email_plain_message = strip_tags(email_html_message)  # Plain text fallback

            # Custom sender name
            from_email = f'"EasyRent Support Team" <{settings.EMAIL_HOST_USER}>'  # 📨

            # Send activation email
            email = EmailMultiAlternatives(
                subject="Activate Your EasyRent Account",
                body=email_plain_message,
                from_email=from_email,
                to=[user.email],
            )
            email.attach_alternative(email_html_message, "text/html")
            email.send(fail_silently=False)

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
            
            # Redirect to the login page
            return HttpResponseRedirect('https://flat-rent-api.onrender.com/api/login/')  # Redirects the user to the login page

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