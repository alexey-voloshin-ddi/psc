from django.db import models


class Account(models.Model):
    owner = models.OneToOneField('users.User', related_name='owner')
    user_contact_information = models.ManyToManyField('users.User', related_name='user_contact_information', blank=True)

    is_active = models.BooleanField(default=True)
    is_multiple_company = models.BooleanField(default=False)
    is_multiple_users = models.BooleanField(default=False)
    deleted_at = models.DateField(blank=True, null=True)

    __origin_is_multiple_company = None
    __origin_is_multiple_users = None

    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)
        self.__origin_is_multiple_company = self.is_multiple_company
        self.__origin_is_multiple_users = self.is_multiple_users

    def __str__(self):
        return self.owner.name if self.owner.name else self.owner.username

    def save(self, *args, **kwargs):
        from psc.notifications.models import Notification
        super(Account, self).save(*args, **kwargs)

        # Create notification when `is_multiple_users is active
        if self.is_multiple_users and self.is_multiple_users != self.__origin_is_multiple_users:
            Notification.objects.create(
                user=self.owner,
                type=Notification.TYPE_MULTIPLE_USER_ACTIVE,
                instance_name=self.__str__()
            )

        # Create notification when `is_multiple_company is active
        if self.is_multiple_company and self.is_multiple_company != self.__origin_is_multiple_company:
            Notification.objects.create(
                user=self.owner,
                type=Notification.TYPE_MULTIPLE_COMPANY_ACTIVE,
                instance_name=self.__str__()
            )

        # Update `is_active status for all users attached to this account
        # if the `is_multiple_users was changed, except owner
        if self.is_multiple_users != self.__origin_is_multiple_users:
            self.user_set.exclude(
                pk=self.pk).update(is_active=self.is_multiple_users)

        # Update `is_active status for all companies attached to this account
        # and all products attached to changed companies
        # if the `is_multiple_company was changed,
        # except first attached company
        if self.is_multiple_company != self.__origin_is_multiple_company:
            first_company = self.company_set.order_by('created_at').first()

            if first_company:
                companies_to_update = self.company_set.exclude(
                    pk=first_company.pk)

                from psc.product.models import Product
                products_to_update = Product.objects.filter(
                    company__in=companies_to_update)

                companies_to_update.update(is_active=self.is_multiple_company)
                products_to_update.update(is_active=self.is_multiple_company)


class ContactInformation(models.Model):
    contact_name = models.CharField(max_length=255)
    email = models.EmailField()
    account = models.ForeignKey(Account, blank=True, null=True)

    def __str__(self):
        return self.contact_name
