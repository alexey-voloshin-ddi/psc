from django.conf.urls import url
from django.views.generic.base import TemplateView

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.UsersList.as_view(),
        name='user-list'
    ),
    url(
        regex=r'^invite/',
        view=views.InviteUserView.as_view()
    ),
    url(
        regex=r'activate/(?P<key>.+)/$',
        view=views.ActivateUserView.as_view(),
        name='activate'
    ),
    url(
        regex=r'registration/$',
        view=views.RegistrationView.as_view(),
        name='registration'
    ),
    url(
        regex=r'registration/done/$',
        view=TemplateView.as_view(template_name='users/registration_done.html')
    ),
    url(
        regex=r'registration/(?P<key>.+)/$',
        view=views.RegistrationView.as_view(),
        name='registration'
    ),
    url(
        regex=r'resend/activation/$',
        view=views.ReSendActivationKey.as_view()
    ),
    url(
        regex=r'resend/activation/done/$',
        view=TemplateView.as_view(
            template_name='users/resend_activation_done.html')
    ),
    url(
        regex=r'^resend/invitation/(?P<pk>[0-9]+)/$',
        view=views.ResendInvitation.as_view(),
        name='resend-invitation'
    )
]
