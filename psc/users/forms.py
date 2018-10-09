import datetime
from django import forms
from django.core.exceptions import ValidationError
from django.db.models.query_utils import Q

from psc.accounts.models import Account
from psc.companies.models import Company
from psc.notifications.models import Notification
from psc.taskapp.tasks import send_activation_email, send_invitation_email
from .models import User
from django.conf import settings
from psc.users.models import ActivateEmailKeys, InvitationKey
from django.contrib.auth.forms import UserChangeForm, UserCreationForm


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User

    def clean_account(self):
        # Check that User can be created and assigned to given account
        account = self.cleaned_data['account']
        if account:
            users_count = account.user_set.count()
            # Check that it's update and have assigned account

            if not self.instance.account or self.instance.account.id != account.id:
                users_count += 1
                # counting that we wanna create or switch
                # to another account

            # Check active invites for this account
            active_invitations = account.owner.invitationkey_set.count()

            # Check that User count not graiter then max count and account can have multiple users
            if account.is_multiple_users and users_count + active_invitations > settings.MAX_USER_PER_ACCOUNT:
                error_msg = 'Selected Account has reach ' \
                            'max count of users ({}). '.format(
                    settings.MAX_USER_PER_ACCOUNT)

                if active_invitations > 0:
                    error_msg += 'There are ({}) active invitation.'.format(
                        active_invitations)
                raise forms.ValidationError(error_msg)

            # If account can have multiple users check that it's only one user for this account
            elif not account.is_multiple_users and users_count > 0:
                raise forms.ValidationError(
                    'Selected Account can have only one User')

        return account

    def clean_email(self):
        # Validate that email is unique
        email = self.cleaned_data['email']
        instance_ids = [self.instance.id] if self.instance else []
        if User.objects.filter(email=email).exclude(
            id__in=instance_ids).exists():
            raise forms.ValidationError('Email already in use.')
        return email


class MyUserCreationForm(UserCreationForm):
    error_message = UserCreationForm.error_messages.update({
        'duplicate_username': 'This username has already been taken.'
    })

    class Meta(UserCreationForm.Meta):
        model = User

    def clean_username(self):
        # Validate that username is unique
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

    def clean_account(self):
        # Check that User can be created and assigned to given account
        account = self.cleaned_data['account']
        if account:
            users_count = account.user_set.all().count()
            # Check that it's update and have assigned account
            if not self.instance.account or self.instance.account.id != account.id:
                users_count += 1  # counting that we wanna create

            # Check that User count not graiter then max count and account can have multiple users
            if account.is_multiple_users and users_count > settings.MAX_USER_PER_ACCOUNT:
                raise forms.ValidationError(
                    'Selected Account has reach max count of users ({})'.format(
                        settings.MAX_USER_PER_ACCOUNT)
                )

            # If account can have multiple users check that it's only one user for this account
            elif not account.is_multiple_users and users_count > 0:
                raise forms.ValidationError(
                    'Selected Account can have only one User')

        return account


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    agree = forms.BooleanField(required=False)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'password', 'email', 'phone',
                  'confirm_password', 'agree')

    def __init__(self, *args, **kwargs):
        self._invitation_key = kwargs.pop('invitation_key')
        try:
            self._invitation = InvitationKey.objects.get(
                key=self._invitation_key)
        except InvitationKey.DoesNotExist:
            self._invitation = None
        self._domain = kwargs.pop('domain')
        self._protocol = kwargs.pop('protocol')
        super().__init__(*args, **kwargs)

    def clean(self):
        if self._invitation_key and not self._invitation:
            raise ValidationError("Invitation does not exist.")

        if self._invitation_key:
            account = self._invitation.user.get_account()
            users_count = account.user_set.all().count()
            if account.is_multiple_users and users_count >= settings.MAX_USER_PER_ACCOUNT:
                raise ValidationError("Account has maximum numbe of users "
                                      "registered already.")
            elif not account.is_multiple_users:
                raise ValidationError("Account can have only one user.")
        return self.cleaned_data

    def clean_confirm_password(self):
        # Check that password and confirm password match
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise forms.ValidationError("Passwords doesn't match.")

        return password

    def clean_agree(self):
        # Check that user agree with terms of user
        agree = self.cleaned_data['agree']

        if not agree:
            raise forms.ValidationError(
                "You must read and agree with terms of service.")

        return agree

    def clean_email(self):
        # Validate that email is unique
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email already registered')
        if self._invitation and email != self._invitation.email:
            raise forms.ValidationError('You can only sign up with the same '
                                        'email that you have been invited to')
        return email

    def save(self, *args, **kwargs):
        # Save new user
        password = self.cleaned_data['password']
        user = super(RegistrationForm, self).save(*args, **kwargs)

        # Set password to user
        user.set_password(password)
        user.username = user.email
        user.name = "{} {}".format(user.first_name, user.last_name)
        user.is_active = False
        user.save()

        if not self._invitation:
            # Create account for new user
            Account.objects.create(owner=user)
            user.access_level = User.ACCESS_LEVEL_OWNER
            user.confirmed = True
        else:
            user.account = self._invitation.user.get_account()
            user.access_level = self._invitation.access_level
            user.confirmed = False
            InvitationKey.objects.filter(id=self._invitation.id).delete()
            Notification.objects.create(
                user=self._invitation.user,
                type=Notification.INVITED_USER_REGISTERED,
                instance_name=user.name
            )
        user.save()

        # Create activation key
        activation_key = ActivateEmailKeys.objects.create(
            user=user,
            created_at=datetime.date.today()).key

        # Send activation email
        send_activation_email.delay(protocol=self._protocol,
                                    domain=self._domain,
                                    key=activation_key,
                                    email_to=user.email)

        return user


class ResendActivationLink(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        # Validate that email was registered in the system
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email doesn't register in system.")

        if User.objects.get(email=email).is_active:
            raise forms.ValidationError("User Already active.")

        return email

    def save(self, request):
        email = self.cleaned_data['email']
        user = User.objects.get(email=email)

        protocol = 'https' if request.is_secure() else 'http'
        domain = request.META['HTTP_HOST']

        # Remove previous activation key
        ActivateEmailKeys.objects.filter(user=user).delete()
        # Create new activation key
        activation_key = ActivateEmailKeys.objects.create(user=user,
                                                          created_at=datetime.date.today()).key
        # Send new activation email
        send_activation_email.delay(protocol=protocol, domain=domain,
                                    key=activation_key, email_to=email)


class InviteForm(forms.ModelForm):
    class Meta:
        model = InvitationKey
        fields = ('email', 'access_level',)

    def __init__(self, *args, **kwargs):
        self._account = kwargs.pop('account')
        self._user = kwargs.pop('user')
        self._domain = kwargs.pop('domain')
        self._protocol = kwargs.pop('protocol')
        super().__init__(*args, **kwargs)

    def clean(self):
        users_count = self._account.user_set.all().count()
        invites_count = InvitationKey.objects.filter(
            Q(user__account=self._account) |
            Q(user__owner=self._account)
        ).distinct().count()
        all_count = users_count + invites_count
        if self._account.is_multiple_users and all_count >= \
            settings.MAX_USER_PER_ACCOUNT:
            raise ValidationError(
                "You can't invite more users, account "
                "reached a maximum number of users and "
                "invitations.")
        elif not self._account.is_multiple_users:
            raise ValidationError("You can't invite more users, an account "
                                  "can only has a single user.")
        return self.cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email']
        if InvitationKey.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Invitation on this email already sent')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'User with such email already registered')
        return email

    def save(self, *args, **kwargs):
        invite_key = InvitationKey.objects.create(
            email=self.cleaned_data['email'],
            user=self._user,
            created_at=datetime.date.today(),
            access_level=self.cleaned_data['access_level']
        )
        send_invitation_email(self._protocol, self._domain, invite_key.key,
                              invite_key.email)
