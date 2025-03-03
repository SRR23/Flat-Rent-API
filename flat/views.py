from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView

from .models import Flat
from .serializers import (
    FlatSerializer,
    MessageSerializer
)

class AddFlatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.user_type != 'owner':  # Only owners can add flats
            return Response({"error": "Only owners can add flats"}, status=status.HTTP_403_FORBIDDEN)

        serializer = FlatSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class OwnerFlatListView(APIView):
    """ List all flats added by the logged-in owner """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.user_type != 'owner':
            return Response({"error": "Only owners can view their flats"}, status=status.HTTP_403_FORBIDDEN)
        
        flats = Flat.objects.filter(owner=request.user)
        serializer = FlatSerializer(flats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class FlatUpdateDeleteView(APIView):
    """ Update or delete a specific flat (only by its owner) """
    permission_classes = [IsAuthenticated]

    def get_object(self, flat_id, user):
        try:
            return Flat.objects.get(id=flat_id, owner=user)
        except Flat.DoesNotExist:
            return None

    def put(self, request, flat_id):
        flat = self.get_object(flat_id, request.user)
        if not flat:
            return Response({"error": "Flat not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FlatSerializer(flat, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, flat_id):
        flat = self.get_object(flat_id, request.user)
        if not flat:
            return Response({"error": "Flat not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)

        flat.delete()
        return Response({"message": "Flat deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class FlatDetailView(RetrieveAPIView):
    queryset = Flat.objects.all()
    serializer_class = FlatSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Anyone can view flat details
    lookup_field = "slug"  # Use flat slug to retrieve details


class FlatListView(ListAPIView):
    queryset = Flat.objects.all()
    serializer_class = FlatSerializer
    permission_classes = [AllowAny]  # Public access


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]  # ✅ Only logged-in renters can send messages

    def post(self, request, slug):
        flat = get_object_or_404(Flat, slug=slug)  # Get the flat using slug
        owner_email = flat.owner.email  # Get owner's email

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            first_name = serializer.validated_data['first_name']
            last_name = serializer.validated_data['last_name']
            email = serializer.validated_data['email']
            phone = serializer.validated_data['phone']
            message = serializer.validated_data['message']

            # 🛠️ Render HTML email template with dynamic data
            email_html_content = render_to_string('emails/booking_email.html', {
                'owner_name': flat.owner.first_name,
                'flat_title': flat.title,
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone,
                'message': message
            })

            subject = f"Message from {first_name} {last_name} - Interested in Your Flat"
            
            # Send email with both HTML & plain text versions
            email_msg = EmailMultiAlternatives(
                subject,
                message,  # Plain text version (fallback)
                settings.EMAIL_HOST_USER,  # ✅ Use sender email dynamically
                [owner_email]
            )
            email_msg.attach_alternative(email_html_content, "text/html")
            email_msg.send()

            return Response({'success': 'Message sent successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
