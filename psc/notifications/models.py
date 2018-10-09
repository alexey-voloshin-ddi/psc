from django.db import models

from psc.users.models import User


class Notification(models.Model):
    TYPE_USER_APPROVED = 1
    TYPE_COMPANY_APPROVED = 2
    TYPE_COMPANY_DENY = 3
    TYPE_PRODUCT_APPROVED = 4
    TYPE_PRODUCT_DENY = 5
    TYPE_MULTIPLE_USER_ACTIVE = 6
    TYPE_MULTIPLE_COMPANY_ACTIVE = 7
    INVITED_USER_REGISTERED = 8
    TYPE_USER_DENY = 9
    TYPE_USER_CONFIRMED = 10
    TYPE_USER_REMOVED = 11
    TYPE_COMPANY_REMOVED = 12
    TYPE_PRODUCT_REMOVED = 13

    STATUS_NEW = 1
    STATUS_READ = 2
    STATUS_ARCHIVED = 3

    STATUS_CHOICES = (
        (STATUS_NEW, 'New'),
        (STATUS_READ, 'Read'),
        (STATUS_ARCHIVED, 'Archived')
    )

    TYPE_CHOICES = (
        (TYPE_USER_APPROVED, 'User Approved'),
        (TYPE_COMPANY_APPROVED, 'Company Approved'),
        (TYPE_COMPANY_DENY, 'Company Deny'),
        (TYPE_PRODUCT_APPROVED, 'Product Approved'),
        (TYPE_PRODUCT_DENY, 'Product Deny'),
        (TYPE_MULTIPLE_USER_ACTIVE, 'Account Multiple users activated'),
        (TYPE_MULTIPLE_COMPANY_ACTIVE, 'Account Multiple company activated'),
        (INVITED_USER_REGISTERED, 'Invited user registered'),
        (TYPE_USER_DENY, 'User Deny'),
        (TYPE_USER_CONFIRMED, 'User Confirmed'),
        (TYPE_USER_REMOVED, 'User Removed'),
        (TYPE_COMPANY_REMOVED, 'Company Removed'),
        (TYPE_PRODUCT_REMOVED, 'Product Removed')
    )

    user = models.ForeignKey(User)
    type = models.SmallIntegerField(choices=TYPE_CHOICES)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_NEW)
    created_at = models.DateTimeField(auto_now_add=True)
    instance_name = models.CharField(max_length=255)

    def __str__(self):
        return "User: {}, Type: {}".format(
            self.user, self.get_type_display()
        )
