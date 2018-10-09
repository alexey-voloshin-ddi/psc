from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_delete
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from psc.core.tokens import psc_tokens
from psc.accounts.models import Account


class AccessLevelMixin(models.Model):
    ACCESS_LEVEL_NONE = None
    ACCESS_LEVEL_OWNER = 1
    ACCESS_LEVEL_EDITOR = 2
    ACCESS_LEVEL_CHOICES = (
        (ACCESS_LEVEL_NONE, 'Choice Access Level'),
        (ACCESS_LEVEL_OWNER, 'Owner'),
        (ACCESS_LEVEL_EDITOR, 'Editor')
    )

    access_level = models.SmallIntegerField(choices=ACCESS_LEVEL_CHOICES, default=ACCESS_LEVEL_EDITOR)

    class Meta:
        abstract = True


class User(AbstractUser, AccessLevelMixin):

    name = models.CharField(_('Name of User'), blank=True, max_length=255)
    account = models.ForeignKey(Account, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)

    confirmed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('User', blank=True, null=True, related_name='user_created_by')

    edited_at = models.DateTimeField(auto_now=True)
    edited_by = models.ForeignKey('User', blank=True, null=True, related_name='user_edited_by')
    is_approved = models.BooleanField(default=False)

    __original_confirmed = None
    __original_approved = None

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.__original_confirmed = self.confirmed
        self.__original_approved = self.is_approved

    def __str__(self):
        return self.username

    def get_account(self):
        account = self.account
        if not account:
            try:
                account = Account.objects.get(owner=self)
            except Account.DoesNotExist:
                return None
        return account

    def is_owner(self):
        return self.access_level == self.ACCESS_LEVEL_OWNER

    def get_absolute_url(self):
        try:
            uri = reverse('users:detail', kwargs={'username': self.username})
        except:
            uri = '/'
        return uri

    def save(self, *args, **kwargs):
        from psc.notifications.models import Notification
        super(User, self).save(*args, **kwargs)

        # create notification when user confirmed
        if self.confirmed and self.confirmed != self.__original_confirmed:
            Notification.objects.create(
                user=self,
                type=Notification.TYPE_USER_CONFIRMED,
                instance_name=self.name
            )

        # create notification when user approved or deny
        if self.is_approved != self.__original_approved:
            notification_type = Notification.TYPE_USER_APPROVED \
                if self.is_approved else Notification.TYPE_USER_DENY

            Notification.objects.create(
                user=self,
                type=notification_type,
                instance_name=self.name
            )


class ActivateEmailKeys(models.Model):
    key = models.CharField(max_length=255)
    user = models.ForeignKey(User)
    created_at = models.DateField()

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        # Set new key if not provided
        if not self.key:
            # Create random string as a key
            self.key = psc_tokens.make_token(self.user)

        return super(ActivateEmailKeys, self).save(*args, **kwargs)


class InvitationKey(AccessLevelMixin):
    key = models.CharField(max_length=255)
    user = models.ForeignKey(User)
    email = models.EmailField()
    created_at = models.DateField()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Set new key if not provided
        if not self.key:
            # Create random string as a key
            self.key = psc_tokens.make_token(self.user)

        return super(InvitationKey, self).save(*args, **kwargs)


def post_delete_user(sender, instance, **kwargs):
    from psc.notifications.models import Notification

    try:
        if instance.account:
            # create notification when user is removed
            Notification.objects.create(
                user=instance.account.owner,
                type=Notification.TYPE_USER_REMOVED,
                instance_name=instance.name
            )
    except:
        pass


post_delete.connect(post_delete_user, User)
