"""
serializers.py

This module contains serializers for the Users app.
It includes serializers for user registration, login, and user details.

The serializers are used to validate and serialize data for the Users app.
- RegisterSerializer: Used for user registration.
- LoginSerializer: Used for user login.
- UserSerializer: Used for serializing user details.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str

from .models import Users


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['user_id', 'email', 'username', 'is_active', 'is_staff', 'is_superuser']
        read_only_fields = ['user_id', 'is_active', 'is_staff', 'is_superuser']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Users
        fields = ['email', 'username', 'password', 'password2']

    def validate_email(self, value):
        validate_email(value)
        if Users.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")

        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Password do not match.'})

        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = Users.objects.create_user(
            email = validated_data['email'],
            username = validated_data['username'],
            password = validated_data['password']
        )

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only = True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid Credentials.")

        data['user'] = user

        return data