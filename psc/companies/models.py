from django.db import models
from psc.accounts.models import Account
from psc.notifications.models import Notification
from psc.users.models import User
from django_countries.fields import CountryField
from psc.core.models import ImageBaseModel
from django.db.models.signals import post_delete, pre_delete


class Company(models.Model):
    name = models.CharField(max_length=255)
    account = models.ForeignKey(Account)
    website = models.URLField()
    short_description = models.CharField(max_length=255)
    description = models.TextField()
    country = CountryField(blank=True, null=True)
    headquarter = models.ForeignKey('Office', related_name='headquarter', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, blank=True, null=True, related_name='company_created_by')

    edited_at = models.DateTimeField(auto_now=True)
    edited_by = models.ForeignKey(User, blank=True, null=True, related_name='company_edited_by')
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    __original_approved = None

    def __init__(self, *args, **kwargs):
        super(Company, self).__init__(*args, **kwargs)
        self.__original_approved = self.is_approved

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Company, self).save(*args, **kwargs)

        # create notification when company approve or deny
        if self.is_approved != self.__original_approved:
            notification_type = Notification.TYPE_COMPANY_APPROVED \
                if self.is_approved else Notification.TYPE_COMPANY_DENY
            user = self.edited_by \
                if self.edited_by and self.created_by != self.edited_by \
                else self.created_by

            Notification.objects.create(
                user=user,
                type=notification_type,
                instance_name=self.name
            )
            self.__original_approved = self.is_approved


class Office(models.Model):
    address = models.TextField()
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip = models.CharField(max_length=16)
    country = CountryField()
    company = models.ForeignKey(Company, related_name='company')

    def __str__(self):
        return self.address


class CompanyImages(ImageBaseModel):
    company = models.ForeignKey(Company, blank=True, null=True)

    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = 'Images'


def set_images_edited_outside(sender, instance, **kwargs):
    try:
        sender.objects.filter(
            company=instance.company,
            product_position=instance.product_position
        ).update(is_edited_outside=True)
    except Company.DoesNotExist:
        pass


def image_delete(sender, instance, **kwargs):
    try:
        instance.path.delete(False)
    except IOError:
        pass


def post_delete_company(sender, instance, **kwargs):
    try:
        # create notification when product is removed
        Notification.objects.create(
            user=instance.account.owner,
            type=Notification.TYPE_COMPANY_REMOVED,
            instance_name=instance.name
        )
    except:
        pass


pre_delete.connect(image_delete, CompanyImages)
post_delete.connect(set_images_edited_outside, CompanyImages)
post_delete.connect(post_delete_company, Company)
