from rest_framework import serializers
from user_profile.models import User
from .models import (
    Flat,
    Category,
    Location
)


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'email']  # Include necessar
        

class FlatSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_title = serializers.StringRelatedField(source='category', read_only=True)
    
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())
    location_title = serializers.StringRelatedField(source='location', read_only=True)
    
    owner = OwnerSerializer(source='owner', read_only=True)  # Nested serializer
    
    
    class Meta:
        model = Flat
        fields = [
            'id',  # Add ID for easier referencing
            'owner',
            'title',
            'slug',
            'category',
            'category_title',
            'location',
            'location_title',
            'flat_size',
            'room',
            'bath',
            'kitchen',
            'image_1',
            'image_2',
            'image_3',
            'image_4',
            'feature_1',
            'feature_2',
            'feature_3',
            'feature_4',
            'feature_5',
            'description_1',
            'description_2',
            'description_3',
            'description_4',
            'description_5',
            'available',
            'created_at',
            'updated_at'
        ]

    def create(self, validated_data):
        
        request = self.context.get('request')
        validated_data['owner'] = request.user  # Assign the logged-in owner
            
        return super().create(validated_data)


    

