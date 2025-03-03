from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Flat
from .serializers import FlatSerializer

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