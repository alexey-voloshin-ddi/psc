from django.conf.urls import url

from psc.product.views import (
    ProductCreateView, UploadFile, ProductList, ProductEditView,
    ProductAutocomplete
)

urlpatterns = [
    url(r'^$', ProductList.as_view(), name='list'),
    url(r'^create/$', ProductCreateView.as_view(), name='create'),
    url(r'^upload/image/$', UploadFile.as_view(), name='upload_image'),
    url(r'^(?P<pk>\d+)/edit/$', ProductEditView.as_view()),

    # autocomplete uri
    url(r'^autocomplete/$', ProductAutocomplete.as_view(), name='autocomplete'),
]
