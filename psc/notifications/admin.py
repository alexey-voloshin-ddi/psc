from django.contrib import admin
from psc.notifications.models import Notification

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created_at')

admin.site.register(Notification, NotificationAdmin)
