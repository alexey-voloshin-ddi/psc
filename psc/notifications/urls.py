from django.conf.urls import url

from psc.notifications.views import NotificationList

urlpatterns = [
    url(r'^$', NotificationList.as_view()),
]
