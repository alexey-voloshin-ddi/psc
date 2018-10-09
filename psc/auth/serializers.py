import datetime
from rest_framework import serializers
from django.contrib.auth import authenticate, login

from psc.accounts.models import Account
from psc.taskapp.tasks import send_activation_email
from psc.users.models import User, ActivateEmailKeys


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255, write_only=True)
    name = serializers.CharField(read_only=True)
    id = serializers.CharField(read_only=True)

    def create(self, validated_data):
        # Handling POST request in create method to login user
        user = authenticate(username=validated_data.get('email'), password=validated_data.get('password'))
        request = self.context['request']
        if user is None:
            raise serializers.ValidationError({'error': 'Wrong email or password'})
        login(request, user)
        return user


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'confirm_password')

    def validate(self, attrs):
        # Validate that passwords match
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError({'password': "Passwords doesn't match."})

        return super(RegistrationSerializer, self).validate(attrs)

    def validate_email(self, value):
        # Validate that email is unique
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email Already in use')
        return value

    def create(self, validated_data):
        # Create new user
        password = validated_data.pop('confirm_password')
        # Generate name of user based on given First name and Last name
        validated_data['name'] = "{} {}".format(validated_data['first_name'], validated_data['last_name'])
        validated_data['username'] = validated_data['email']
        # Make user inactive
        validated_data['is_active'] = False

        # Create user
        user = super(RegistrationSerializer, self).create(validated_data)

        # Set user password
        user.set_password(password)

        # Create new account for user
        Account.objects.create(owner=user)

        request = self.context['request']

        protocol = 'https' if request.is_secure() else 'http'
        domain = request.META['HTTP_HOST']
        # Create Activation key for user
        activation_key = ActivateEmailKeys.objects.create(user=user, created_at=datetime.date.today()).key

        # Send email to user
        send_activation_email.delay(protocol=protocol, domain=domain, key=activation_key, email_to=user.email)

        return user

