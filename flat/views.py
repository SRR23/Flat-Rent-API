

from rest_framework.generics import RetrieveAPIView, ListAPIView, DestroyAPIView
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny,
)
from rest_framework.exceptions import ValidationError
from django.db.models import Q, Exists, OuterRef
from rest_framework.response import Response
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework import status, pagination
from rest_framework.views import APIView

from .models import (
    Flat, 
    Category, 
    Location
)
from .serializers import (
    FlatSerializer, 
    MessageSerializer,
    CategorySerializer,
    LocationSerializer,
    ContactFormSerializer
    
)


# Custom pagination class
class PaginationView(pagination.PageNumberPagination):
    page_size = 2  # Default page size
    page_size_query_param = 'page_size'

    def get_max_page_size(self, total_records):
        """Dynamically set max page size based on total records."""
        return max(50, total_records // 2)  # Ensures at least 50

    def paginate_queryset(self, queryset, request, view=None):
        total_records = len(queryset)  # Total data count
        self.max_page_size = self.get_max_page_size(total_records)  # Set max dynamically
        return super().paginate_queryset(queryset, request, view)
    
    def get_paginated_response(self, data):
        """Customize paginated response to include page links."""
        return Response({
            "count": self.page.paginator.count,  # Total items
            "total_pages": self.page.paginator.num_pages,  # Total pages
            "current_page": self.page.number,  # Current page number
            "page_size": self.page.paginator.per_page,  # Items per page
            "next": self.get_next_link(),  # Next page URL
            "previous": self.get_previous_link(),  # Previous page URL
            "results": data  # Paginated results
        })


class HomeView(ListAPIView):
    
    queryset = (
        Flat.objects.select_related("owner", "category", "location")
        # .prefetch_related("renters_who_messaged")
        .order_by("-created_at")[:6]  # Limit to latest 6 flats
    )
    serializer_class = FlatSerializer
    permission_classes = [AllowAny]

# List all Categories
class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer 
    
    
# List all Location
class LocationListView(ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer 
    

class AddFlatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.user_type != "owner":  # Only owners can add flats
            return Response(
                {"error": "Only owners can add flats"}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = FlatSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OwnerFlatListView(ListAPIView):
    """List all flats added by the logged-in owner"""

    serializer_class = FlatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.user_type != "owner":
            return Flat.objects.none()  # Return an empty queryset instead of filtering

        return (
            Flat.objects.filter(owner=user)
            .select_related("owner","category", "location")
            # .prefetch_related("renters_who_messaged")
            .order_by("-created_at")  # Show newest flats first
        )

    def list(self, request, *args, **kwargs):
        if request.user.user_type != "owner":
            return Response(
                {"error": "Only owners can view their flats"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().list(request, *args, **kwargs)



class OwnerFlatUpdateDeleteView(APIView):
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

        serializer = FlatSerializer(flat, data=request.data, partial=True, context={"request": request})
        
        if serializer.is_valid():
            # 🔹 Avoid extra queries by manually updating fields
            for attr, value in serializer.validated_data.items():
                setattr(flat, attr, value)

            flat.save()  # 🔹 Only one save query instead of multiple updates

            return Response(FlatSerializer(flat).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, flat_id):
        flat = self.get_object(flat_id, request.user)
        if not flat:
            return Response({"error": "Flat not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)

        flat.delete()
        return Response({"message": "Flat deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class RenterBookingListView(ListAPIView):
    """✅ View for renters to see their booked flats"""

    permission_classes = [IsAuthenticated]  # Only logged-in renters
    serializer_class = FlatSerializer

    def get_queryset(self):
        return (
            self.request.user.messaged_flats
            .select_related("category", "location", "owner")  # Optimize foreign keys
            # .prefetch_related("renters_who_messaged")
            .order_by("-created_at")  # Show newest bookings first
        )


class RenterBookingDeleteView(DestroyAPIView):
    """✅ Optimized view for renters to delete their booking"""

    permission_classes = [IsAuthenticated]

    def delete(self, request, slug):
        # 🔹 Check if the user has booked the flat using a single query
        flat = Flat.objects.filter(
            slug=slug, renters_who_messaged=request.user
        ).first()

        # 🔹 If the flat exists in the filter, the renter has booked it
        if flat:
            flat.renters_who_messaged.remove(request.user)  # Remove renter
            return Response(
                {"success": "Booking removed"}, status=status.HTTP_204_NO_CONTENT
            )

        return Response(
            {"error": "You have not booked this flat"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class FlatDetailView(RetrieveAPIView):
    queryset = Flat.objects.select_related(
        "owner", "category", "location"
    ).prefetch_related("renters_who_messaged")
    serializer_class = FlatSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly
    ]  # Anyone can view, but modifications require authentication
    lookup_field = "slug"  # Retrieve flat details using the slug


class FlatListView(ListAPIView):
    pagination_class = PaginationView  # Default pagination class
    queryset = (
        Flat.objects.select_related("owner", "category", "location")
        # .prefetch_related("renters_who_messaged")
        .order_by("-created_at")
    )
    serializer_class = FlatSerializer
    permission_classes = [AllowAny]



class SendMessageView(APIView):
    """✅ View for renters to send messages to flat owners"""

    permission_classes = [IsAuthenticated]  # Only logged-in renters

    def post(self, request, slug):
        """Handles message sending from renter to flat owner"""

        # Optimize query by checking if the renter already messaged using Exists()
        flat = (
            Flat.objects.annotate(
                already_messaged=Exists(
                    Flat.renters_who_messaged.through.objects.filter(
                        flat_id=OuterRef("pk"), user_id=request.user.id
                    )
                )
            )
            .select_related("owner")  # Optimize foreign key lookup
            .get(slug=slug)
        )

        if flat.already_messaged:
            return Response(
                {"error": "You have already sent a message for this flat."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            owner_email = flat.owner.email  # Get owner's email

            # Render HTML email template with dynamic data
            email_html_content = render_to_string(
                "emails/booking_email.html",
                {
                    "owner_name": flat.owner.first_name,
                    "flat_title": flat.title,
                    "first_name": validated_data["first_name"],
                    "last_name": validated_data["last_name"],
                    "email": validated_data["email"],
                    "phone": validated_data["phone"],
                    "message": validated_data["message"],
                },
            )

            subject = f"Message from {validated_data['first_name']} {validated_data['last_name']} - Interested in Your Flat"

            # Send email with both HTML & plain text versions
            email_msg = EmailMultiAlternatives(
                subject,
                validated_data["message"],  # Plain text version (fallback)
                f"EasyRent Support Team <{settings.EMAIL_HOST_USER}>",  # ✅ Shows "EasyRent" before sender email
                [owner_email],
            )
            email_msg.attach_alternative(email_html_content, "text/html")
            email_msg.send()

            # 🔹 Mark renter as someone who has already sent a message (optimized bulk update)
            flat.renters_who_messaged.add(request.user)

            return Response(
                {"success": "Message sent successfully"}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Filter Blogs by category
class FlatCategoryFilterView(ListAPIView):
    serializer_class = FlatSerializer
    pagination_class = PaginationView  # Default pagination class

    def get_queryset(self):
        category_id = self.request.query_params.get("category")

        if not category_id:
            raise ValidationError({"error": "Category ID is required."})

        return (
            Flat.objects.select_related("category", "location", "owner")
            # .prefetch_related("renters_who_messaged")
            .filter(category_id=category_id)
            .order_by("-created_at")  # Show newest flats first
        )


# 🔍 Why Not Use SearchFilter?
# The SearchFilter from Django REST Framework (DRF) is great for full-text search across multiple fields
# using a single query parameter. However, in your case, you need filtering by specific fields
# (category and location separately), which is better handled using Django's filter() method.


class FlatSearchView(ListAPIView):
    serializer_class = FlatSerializer
    pagination_class = PaginationView  # Default pagination class

    def get_queryset(self):
        queryset = Flat.objects.select_related(
            "category", "location", "owner"
        ).order_by("-created_at")  # Show newest flats first
        
        # .prefetch_related("renters_who_messaged")

        category_query = self.request.query_params.get("category", None)
        location_query = self.request.query_params.get("location", None)

        if category_query and location_query:
            queryset = queryset.filter(
                Q(category__title__icontains=category_query)  # Filter by category
                & Q(location__title__icontains=location_query)  # Filter by location
            )
        elif category_query:
            queryset = queryset.filter(Q(category__title__icontains=category_query))
        elif location_query:
            queryset = queryset.filter(Q(location__title__icontains=location_query))

        return queryset.distinct()


class ContactFormView(APIView):
    def post(self, request):
        serializer = ContactFormSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data["name"]
            email = serializer.validated_data["email"]
            phone = serializer.validated_data["phone"]
            address = serializer.validated_data["address"]
            message = serializer.validated_data["message"]

            # Render email template
            email_body = render_to_string('emails/contact_email.html', {
                'name': name,
                'email': email,
                'phone': phone,
                'address': address,
                'message': message,
            })

            send_mail(
                subject=f"New Contact Message from {name}",
                message="This is a plain text fallback message.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=['iamremon807@gmail.com'],
                html_message=email_body,  # HTML formatted email
            )

            return Response({"message": "Email sent successfully!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
