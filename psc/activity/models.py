from django.db import models


# Create your models here.
from psc.users.models import User


class Summary(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.created_at)


class LogLine(models.Model):
    TYPE_CREATED = 1
    TYPE_EDITED = 2

    TYPE_CHOICES = (
        (TYPE_CREATED, 'Created'),
        (TYPE_EDITED, 'Edited')
    )

    INSTANCE_TYPE_PRODUCT = 1
    INSTANCE_TYPE_USER = 2
    INSTANCE_TYPE_COMPANY = 3

    INSTANCE_TYPE_CHOICES = (
        (INSTANCE_TYPE_PRODUCT, 'Product'),
        (INSTANCE_TYPE_USER, 'User'),
        (INSTANCE_TYPE_COMPANY, 'Company'),

    )

    summary = models.ForeignKey(Summary)
    user = models.ForeignKey(User)
    type = models.SmallIntegerField(choices=TYPE_CHOICES)
    instance_type = models.SmallIntegerField(choices=INSTANCE_TYPE_CHOICES)
    instance_name = models.CharField(max_length=255)
    instance_id = models.IntegerField(blank=True, null=True)
    updated_at = models.DateTimeField()

    def __str__(self):
        return "Log of summary {}".format(self.summary.created_at)

