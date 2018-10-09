from django.views.generic.list import ListView
from django.db.models import Q
from psc.notifications.models import Notification


class NotificationList(ListView):
    template_name = 'notifications/list.html'

    def get_queryset(self):
        account = self.request.user.get_account()
        notifications = Notification.objects.filter(
            Q(user__account=account) |
            Q(user__owner=account)
        ).order_by('-created_at')
        return notifications
