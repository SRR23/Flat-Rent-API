from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)
    house_holding_number = serializers.CharField(required=False, write_only=True)
    address = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = [
            'user_type', 'first_name', 'last_name', 'email', 'phone_number', 
            'password', 'confirm_password', 'house_holding_number', 'address'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        """✅ Ensure passwords match & required fields are filled based on user_type"""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        user_type = data['user_type'].lower()  # Normalize user type
        if user_type == "owner":  
            if not data.get('house_holding_number') or not data.get('address'):
                raise serializers.ValidationError(
                    {"error": "Owners must provide house holding number and address."}
                )
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # Remove confirm_password before creating the user

        house_holding_number = validated_data.pop('house_holding_number', None)
        address = validated_data.pop('address', None)

        user = User.objects.create_user(**validated_data)

        # ✅ Store extra fields for owners
        if user.user_type.lower() == "owner":
            user.house_holding_number = house_holding_number
            user.address = address
            user.save()

        return user




class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'user_type', 'first_name', 'last_name', 'phone_number', 'email']
        read_only_fields = ['email']

    def to_representation(self, instance):
        """✅ Dynamically include extra fields for owners"""
        data = super().to_representation(instance)

        if instance.user_type == "owner":
            data['house_holding_number'] = instance.house_holding_number
            data['address'] = instance.address

        return data
