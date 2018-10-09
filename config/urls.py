from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
from rest_framework import routers
from psc.auth.views import LoginApiView, RegistrationView, Logout
from psc.api.views import CategoryViewSet, CompanyViewSet, AccountViewSet, InvitationViewSet, UserViewSet, \
    NotificationViewSet, ProductViewSet

router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'company', CompanyViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'invitations', InvitationViewSet)
router.register(r'notifications', NotificationViewSet, base_name='notifications')
router.register(r'users', UserViewSet, base_name='users')
router.register(r'products', ProductViewSet)

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),

    url(r'^users/', include('psc.users.urls', namespace='users')),
    url(r'^account/', include('psc.accounts.urls', namespace='accounts')),
    url(r'^companies/', include('psc.companies.urls', namespace='companies')),
    url(r'^notifications/', include('psc.notifications.urls', namespace='notifications')),
    url(r'^products/', include('psc.product.urls', namespace='product')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Your stuff: custom urls includes go here
    url(r'api/v1/login', LoginApiView.as_view({'post': 'login'})),
    url(r'api/v1/registration', RegistrationView.as_view({'post': 'registration'})),
    url(r'api/v1/logout', Logout.as_view({'get': 'api_logout'})),
    url(r'api/v1/', include(router.urls))

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
