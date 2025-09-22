from rest_framework import serializers
from user_profile.models import User
from flat.models import Flat, Category, Location, Family, Bachelor, Shop
import logging

logger = logging.getLogger(__name__)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'title']

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'email']


class FlatSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source='location', write_only=True
    )

    # Family-specific fields
    bed_room = serializers.IntegerField(required=False, allow_null=True)
    dining_room = serializers.BooleanField(required=False, default=True)
    drawing_room = serializers.BooleanField(required=False, default=True)
    balcony = serializers.BooleanField(required=False, default=False)
    rent = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True)

    # Bachelor-specific fields
    available_seats = serializers.CharField(max_length=50, required=False, allow_blank=True)
    dining_charge = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    meal_rate_range = serializers.CharField(max_length=100, required=False, allow_blank=True)
    extra_cost_range = serializers.CharField(max_length=100, required=False, allow_blank=True)
    expected_total_cost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    total_members = serializers.CharField(max_length=50, required=False, allow_blank=True)
    khala_facility = serializers.BooleanField(required=False, default=True, allow_null=True)

    # Shop-specific fields
    square_feet = serializers.IntegerField(required=False, allow_null=True)
    preaching_space = serializers.BooleanField(required=False, default=True, allow_null=True)

    class Meta:
        model = Flat
        fields = [
            'id', 'owner', 'category', 'category_id', 'location', 'location_id',
            'title', 'slug', 'washroom', 'commode', 'water_supply', 'floor', 'tiles',
            'kitchen', 'cctv', 'roof_top_uses', 'garage', 'image_1', 'image_2',
            'image_3', 'image_4', 'image_5', 'created_at', 'updated_at',
            'bed_room', 'dining_room', 'drawing_room', 'balcony', 'rent', 'address',
            'available_seats', 'dining_charge', 'meal_rate_range', 'extra_cost_range',
            'expected_total_cost', 'total_members', 'khala_facility', 'square_feet',
            'preaching_space'
        ]
        read_only_fields = ['owner', 'slug', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.debug(f"Serializer initialized with initial data: {getattr(self, 'initial_data', 'None')}")

    def to_representation(self, instance):
        """Customize the response to include only relevant fields based on category."""
        representation = super().to_representation(instance)
        flat_type = instance.category.title

        # Define fields for each flat type
        common_fields = [
            'id', 'owner', 'category', 'location', 'title', 'slug', 'washroom', 'commode',
            'water_supply', 'floor', 'tiles', 'kitchen', 'cctv', 'roof_top_uses',
            'garage', 'image_1', 'image_2', 'image_3', 'image_4', 'image_5',
            'created_at', 'updated_at'
        ]
        type_specific_fields = {
            'Family': ['bed_room', 'dining_room', 'drawing_room', 'balcony', 'rent', 'address'],
            'Bachelor': ['available_seats', 'dining_charge', 'meal_rate_range', 'extra_cost_range',
                        'expected_total_cost', 'total_members', 'khala_facility'],
            'Shop': ['rent', 'square_feet', 'preaching_space', 'address']
        }

        # Populate type-specific fields from related models
        if flat_type == 'Family' and instance.family_details.exists():
            family = instance.family_details.first()
            representation.update({
                'bed_room': family.bed_room,
                'dining_room': family.dining_room,
                'drawing_room': family.drawing_room,
                'balcony': family.balcony,
                'rent': family.rent,
                'address': family.address
            })
        elif flat_type == 'Bachelor' and instance.bachelor_details.exists():
            bachelor = instance.bachelor_details.first()
            representation.update({
                'available_seats': bachelor.available_seats,
                'dining_charge': bachelor.dining_charge,
                'meal_rate_range': bachelor.meal_rate_range,
                'extra_cost_range': bachelor.extra_cost_range,
                'expected_total_cost': bachelor.expected_total_cost,
                'total_members': bachelor.total_members,
                'khala_facility': bachelor.khala_facility
            })
        elif flat_type == 'Shop' and instance.shop_details.exists():
            shop = instance.shop_details.first()
            representation.update({
                'rent': shop.rent,
                'square_feet': shop.square_feet,
                'preaching_space': shop.preaching_space,
                'address': shop.address
            })

        # Filter the response to include only relevant fields
        filtered_representation = {
            key: representation[key]
            for key in common_fields + type_specific_fields.get(flat_type, [])
            if key in representation
        }

        return filtered_representation

    def validate(self, data):
        """Validate that only relevant fields are provided based on the category."""
        logger.debug(f"Raw data before validation: {data}")

        # Get the category title from category_id
        category = data.get('category')
        if not category:
            raise serializers.ValidationError("The 'category_id' field is required.")
        flat_type = category.title
        logger.debug(f"Inferred type from category: {flat_type}")

        if not flat_type:
            raise serializers.ValidationError("Category title cannot be empty.")

        # Define required and valid fields for each type
        required_fields = {
            'Family': ['bed_room', 'rent', 'address'],
            'Bachelor': ['available_seats', 'dining_charge', 'meal_rate_range', 'extra_cost_range',
                        'expected_total_cost', 'total_members'],
            'Shop': ['rent', 'square_feet', 'address']
        }
        valid_fields = {
            'Family': ['bed_room', 'dining_room', 'drawing_room', 'balcony', 'rent', 'address'],
            'Bachelor': ['available_seats', 'dining_charge', 'meal_rate_range', 'extra_cost_range',
                        'expected_total_cost', 'total_members', 'khala_facility'],
            'Shop': ['rent', 'square_feet', 'preaching_space', 'address']
        }

        # Preprocess payload to convert empty strings and False to None for non-relevant fields
        processed_data = data.copy()
        for field in valid_fields['Family'] + valid_fields['Bachelor'] + valid_fields['Shop']:
            if field in processed_data and field not in valid_fields.get(flat_type, []):
                if processed_data[field] == '' or processed_data[field] is False:
                    processed_data[field] = None
        logger.debug(f"Processed data: {processed_data}")

        # Filter out non-relevant fields
        filtered_data = {
            k: v for k, v in processed_data.items()
            if k in ['title', 'category', 'category_id', 'location', 'location_id', 'washroom',
                     'commode', 'water_supply', 'floor', 'tiles', 'kitchen', 'cctv',
                     'roof_top_uses', 'garage', 'image_1', 'image_2', 'image_3', 'image_4',
                     'image_5'] or k in valid_fields.get(flat_type, [])
        }
        logger.debug(f"Filtered data: {filtered_data}")

        # Get provided detail fields
        detail_fields = [
            field for field in valid_fields['Family'] + valid_fields['Bachelor'] + valid_fields['Shop']
            if field in filtered_data and filtered_data[field] is not None
        ]

        if not detail_fields:
            raise serializers.ValidationError("At least one detail field is required for the specified category.")

        # Check if the type is valid
        if flat_type not in required_fields:
            raise serializers.ValidationError(f"Invalid category title '{flat_type}'. Must be 'Family', 'Bachelor', or 'Shop'.")

        # Validate required fields
        missing_fields = [
            field for field in required_fields[flat_type]
            if field not in filtered_data or filtered_data[field] is None or filtered_data[field] == ''
        ]
        if missing_fields:
            raise serializers.ValidationError(f"Missing required fields for category '{flat_type}': {missing_fields}")

        # Check for invalid fields
        invalid_fields = [field for field in detail_fields if field not in valid_fields[flat_type]]
        if invalid_fields:
            raise serializers.ValidationError(f"Invalid fields for category '{flat_type}': {invalid_fields}")

        return filtered_data

    def create(self, validated_data):
        """Create a flat with associated details based on category."""
        flat_type = validated_data['category'].title

        # Define type-specific fields to remove before creating Flat instance
        type_specific_fields = {
            'Family': ['bed_room', 'dining_room', 'drawing_room', 'balcony', 'rent', 'address'],
            'Bachelor': ['available_seats', 'dining_charge', 'meal_rate_range', 'extra_cost_range',
                        'expected_total_cost', 'total_members', 'khala_facility'],
            'Shop': ['rent', 'square_feet', 'preaching_space', 'address']
        }

        # Remove type-specific fields from validated_data for Flat creation
        flat_data = {k: v for k, v in validated_data.items() if k not in type_specific_fields[flat_type]}
        logger.debug(f"Flat creation data: {flat_data}")

        # Get the owner from the serializer's save kwargs
        owner = self.context['request'].user if self.context.get('request') else None
        if not owner or not owner.is_authenticated:
            raise serializers.ValidationError("A valid authenticated user is required as the owner.")

        # Add owner to flat_data
        flat_data['owner'] = owner

        instance = Flat.objects.create(**flat_data)

        if flat_type == 'Family':
            Family.objects.create(
                flat=instance,
                bed_room=validated_data['bed_room'],
                dining_room=validated_data.get('dining_room', True),
                drawing_room=validated_data.get('drawing_room', True),
                balcony=validated_data.get('balcony', False),
                rent=validated_data['rent'],
                address=validated_data['address']
            )
        elif flat_type == 'Bachelor':
            Bachelor.objects.create(
                flat=instance,
                available_seats=validated_data['available_seats'],
                dining_charge=validated_data['dining_charge'],
                meal_rate_range=validated_data['meal_rate_range'],
                extra_cost_range=validated_data['extra_cost_range'],
                expected_total_cost=validated_data['expected_total_cost'],
                total_members=validated_data['total_members'],
                khala_facility=validated_data.get('khala_facility', True)
            )
        elif flat_type == 'Shop':
            Shop.objects.create(
                flat=instance,
                rent=validated_data['rent'],
                square_feet=validated_data['square_feet'],
                preaching_space=validated_data.get('preaching_space', True),
                address=validated_data['address']
            )

        return instance

    def update(self, instance, validated_data):
        """Update a flat and its associated details based on category."""
        flat_type = validated_data.get('category', instance.category).title

        # Remove type-specific fields for Flat update
        type_specific_fields = {
            'Family': ['bed_room', 'dining_room', 'drawing_room', 'balcony', 'rent', 'address'],
            'Bachelor': ['available_seats', 'dining_charge', 'meal_rate_range', 'extra_cost_range',
                        'expected_total_cost', 'total_members', 'khala_facility'],
            'Shop': ['rent', 'square_feet', 'preaching_space', 'address']
        }
        flat_data = {k: v for k, v in validated_data.items() if k not in type_specific_fields[flat_type]}

        # Get the owner from the serializer's save kwargs
        owner = self.context['request'].user if self.context.get('request') else None
        if not owner or not owner.is_authenticated:
            raise serializers.ValidationError("A valid authenticated user is required as the owner.")
        flat_data['owner'] = owner

        # Update Flat instance fields
        for attr, value in flat_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Clear existing details based on the original type
        if instance.family_details.exists():
            instance.family_details.all().delete()
        elif instance.bachelor_details.exists():
            instance.bachelor_details.all().delete()
        elif instance.shop_details.exists():
            instance.shop_details.all().delete()

        # Create new details based on the new type
        if flat_type == 'Family':
            Family.objects.create(
                flat=instance,
                bed_room=validated_data.get('bed_room'),
                dining_room=validated_data.get('dining_room', True),
                drawing_room=validated_data.get('drawing_room', True),
                balcony=validated_data.get('balcony', False),
                rent=validated_data.get('rent'),
                address=validated_data.get('address')
            )
        elif flat_type == 'Bachelor':
            Bachelor.objects.create(
                flat=instance,
                available_seats=validated_data['available_seats'],
                dining_charge=validated_data['dining_charge'],
                meal_rate_range=validated_data['meal_rate_range'],
                extra_cost_range=validated_data['extra_cost_range'],
                expected_total_cost=validated_data['expected_total_cost'],
                total_members=validated_data['total_members'],
                khala_facility=validated_data.get('khala_facility', True)
            )
        elif flat_type == 'Shop':
            Shop.objects.create(
                flat=instance,
                rent=validated_data['rent'],
                square_feet=validated_data['square_feet'],
                preaching_space=validated_data.get('preaching_space', True),
                address=validated_data['address']
            )

        return instance

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