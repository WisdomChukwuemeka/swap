from rest_framework import serializers
from .models import User, Profile
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'date_joined',
                  'is_staff', 'is_superuser', 'is_active', 'agreement',
                  ]
        read_only_fields = ['id', 'date_joined', 'is_staff', 'is_superuser', 'is_active']

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True, write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'role', 'agreement']
        
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs
        
    
    def validate_role(self, value):
        if not value:
            raise serializers.ValidationError("Role can't be left empty")
        return value
    
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            email = validated_data['email'],
            password = validated_data['password'],
            role = validated_data['role'],
            agreement = validated_data['agreement'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            
            if not user:
                raise serializers.ValidationError("User does not exist")
            if not user.is_active:
                raise serializers.ValidationError("user account has been disabled, contact customer care.")
            attrs['user'] = user
            return attrs
        
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'avatar', 'user', 'full_name', 'phone_number', 'bio', 'address', 'created_at']
        read_only_fields = ['id', 'avatar', 'created_at']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'avatar', 'user', 'full_name', 'phone_number', 'bio', 'address', 'created_at']
        
    def validate_avatar(self, value):
        ext = value.name.split('.')[-1].lower()
        if ext not in ['jpeg', 'jpg', 'png']:
            raise serializers.ValidationError("File not supported. Use jpg, jpeg or png.")
        return value
    
    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar and hasattr(obj.avatar, 'url'):
            media_url = obj.avatar.url.replace('/media/', '/api/media/')
            return request.build_absolute_uri(media_url)
        return None