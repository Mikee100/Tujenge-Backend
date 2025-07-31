# chama_app/serializers.py
from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import AuthenticationFailed
from datetime import timedelta
from django.utils import timezone
from .models import Chama
from .models import Contribution

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        try:
            chama = Chama.objects.get(name="chama1")
        except Chama.DoesNotExist:
            raise serializers.ValidationError("Default chama 'chama1' does not exist.")
        user = User.objects.create_user(**validated_data)
        user.chama = chama
        user.save()
        return user


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['email'] = user.email
        return token

    def validate(self, attrs):
        attrs['username'] = attrs.get('email')
        data = super().validate(attrs)

        if not self.user.is_verified:
            raise AuthenticationFailed("Please verify your account with the OTP sent to your email.")

        # Add these lines:
        data['role'] = self.user.role
        data['is_verified'] = self.user.is_verified
        data['email'] = self.user.email

        return data
class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        if user.is_verified:
            raise serializers.ValidationError("User already verified.")

        if user.otp != otp:
            raise serializers.ValidationError("Invalid OTP.")

        expiration_time = user.otp_created_at + timedelta(minutes=10)
        if timezone.now() > expiration_time:
            raise serializers.ValidationError("OTP has expired.")

        data['user'] = user
        return data
    
class RoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['role']

class ChamaMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'is_verified']

class ChamaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chama
        fields = ['id', 'name', 'description', 'created_at']

class ContributionSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Contribution
        fields = ['id', 'amount', 'month', 'chama', 'user', 'user_email', 'date']
        read_only_fields = ['user', 'date']


from .models import Loan

class LoanSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    approved_by_email = serializers.EmailField(source='approved_by.email', read_only=True)
    
    class Meta:
        model = Loan
        fields = ['id', 'amount', 'purpose', 'status', 'requested_date', 'approved_date', 'user_email', 'approved_by_email', 'chama']
        read_only_fields = ['user', 'status', 'requested_date', 'approved_date', 'approved_by']