from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        regex=r'^$',
        view=views.AccountSettings.as_view()
    ),
    url(
        regex=r'^test_owner_summary/$',
        view=views.TestOwnerEmail.as_view(),
        name='owner_summary'
    ),
    url(
        regex=r'^test_summary_log/$',
        view=views.TestSummaryLog.as_view(),
        name='log_summary'
    ),
    url(
        regex=r'^test_admin_summary/$',
        view=views.TestSummaryEmail.as_view(),
        name='admin_summary'
    )
]
