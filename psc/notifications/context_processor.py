from psc.notifications.models import Notification
from django.db.models import Q


def new_notifications_count(request):
    notification_count = 0
    if request.user.is_authenticated():
        account = request.user.get_account()
        if account:
            notification_count = Notification.objects.filter(
                Q(user__account=account) | Q(user__owner=account),
                status=Notification.STATUS_NEW).count()
    return {'new_notification_count': notification_count}
