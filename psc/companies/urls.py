from django.conf.urls import url

from psc.companies.views import (
    CompanyListView, CompanyAddView, CompanyEditView, CompanyAutocomplete)

urlpatterns = [
    url(r'^$', CompanyListView.as_view(), name='company_list'),
    url(r'^create', CompanyAddView.as_view(), name='company_create'),
    url(r'^(?P<pk>\d+)/edit/', CompanyEditView.as_view(), name='company_edit'),

    # autocomplete uri
    url(r'^autocomplete/$', CompanyAutocomplete.as_view(), name='autocomplete'),
]
