from rest_framework import serializers
from user_profile.models import User
from flat.models import (
    Flat,
    Category,
    Location,
    Family,
    Bachelor,
    Shop
)

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']

# Location Serializer
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'title', 'slug']

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'email']

class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = ['id', 'bed_room', 'dining_room', 'drawing_room', 'balcony', 'rent', 'address']

class BachelorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bachelor
        fields = ['id', 'available_seats', 'dining_charge', 'meal_rate_range', 
                 'extra_cost_range', 'expected_total_cost', 'total_members', 'khala_facility']

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'rent', 'square_feet', 'preaching_space', 'address']

class FlatSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer(read_only=True)
    renters_who_messaged = OwnerSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source='location', write_only=True
    )
    family_details = FamilySerializer(many=True, read_only=False, required=False)
    bachelor_details = BachelorSerializer(many=True, read_only=False, required=False)
    shop_details = ShopSerializer(many=True, read_only=False, required=False)

    class Meta:
        model = Flat
        fields = [
            'id', 'owner', 'renters_who_messaged', 'category', 'category_id',
            'location', 'location_id', 'title', 'slug', 'washroom', 'commode',
            'water_supply', 'floor', 'tiles', 'kitchen', 'cctv', 'roof_top_uses',
            'garage', 'image_1', 'image_2', 'image_3', 'image_4', 'image_5',
            'created_at', 'updated_at', 'family_details', 'bachelor_details', 'shop_details'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Ensure only one type of details (family, bachelor, or shop) is provided
        and matches the category.
        """
        family_data = data.get('family_details')
        bachelor_data = data.get('bachelor_details')
        shop_data = data.get('shop_details')
        category = data.get('category')

        # Count the number of detail types provided
        provided_details = sum(1 for d in [family_data, bachelor_data, shop_data] if d)

        if provided_details == 0:
            raise serializers.ValidationError(
                "At least one of family_details, bachelor_details, or shop_details must be provided."
            )
        if provided_details > 1:
            raise serializers.ValidationError(
                "Only one type of details (family_details, bachelor_details, or shop_details) is allowed."
            )

        # Validate that the provided details match the category
        if family_data and category.title != "Family":
            raise serializers.ValidationError(
                "family_details can only be provided for Family category."
            )
        if bachelor_data and category.title != "Bachelor":
            raise serializers.ValidationError(
                "bachelor_details can only be provided for Bachelor category."
            )
        if shop_data and category.title != "Shop":
            raise serializers.ValidationError(
                "shop_details can only be provided for Shop category."
            )

        return data

    def create(self, validated_data):
        # Extract nested data if provided
        family_data = validated_data.pop('family_details', None)
        bachelor_data = validated_data.pop('bachelor_details', None)
        shop_data = validated_data.pop('shop_details', None)
        
        # Extract category and location
        category_id = validated_data.pop('category')
        location_id = validated_data.pop('location')
        
        # Create the Flat instance
        flat = Flat.objects.create(category=category_id, location=location_id, **validated_data)
        
        # Create Family instances if provided
        if family_data:
            for family_item in family_data:
                Family.objects.create(flat=flat, **family_item)
        
        # Create Bachelor instances if provided
        if bachelor_data:
            for bachelor_item in bachelor_data:
                Bachelor.objects.create(flat=flat, **bachelor_item)
        
        # Create Shop instances if provided
        if shop_data:
            for shop_item in shop_data:
                Shop.objects.create(flat=flat, **shop_item)
        
        return flat

    def update(self, instance, validated_data):
        # Extract nested data if provided
        family_data = validated_data.pop('family_details', None)
        bachelor_data = validated_data.pop('bachelor_details', None)
        shop_data = validated_data.pop('shop_details', None)
        
        # Extract category and location
        category_id = validated_data.pop('category', None)
        location_id = validated_data.pop('location', None)
        
        if category_id:
            instance.category = category_id
        if location_id:
            instance.location = location_id
            
        # Update Family details if provided
        if family_data is not None:
            instance.family_details.all().delete()
            for family_item in family_data:
                Family.objects.create(flat=instance, **family_item)
        
        # Update Bachelor details if provided
        if bachelor_data is not None:
            instance.bachelor_details.all().delete()
            for bachelor_item in bachelor_data:
                Bachelor.objects.create(flat=instance, **bachelor_item)
        
        # Update Shop details if provided
        if shop_data is not None:
            instance.shop_details.all().delete()
            for shop_item in shop_data:
                Shop.objects.create(flat=instance, **shop_item)
        
        return super().update(instance, validated_data)


class MessageSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    message = serializers.CharField(max_length=1000)


class ContactFormSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    address = serializers.CharField(max_length=255, required=False)
    message = serializers.CharField()
    

