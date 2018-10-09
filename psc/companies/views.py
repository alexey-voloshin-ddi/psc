from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.conf import settings
from dal import autocomplete

from psc.companies.forms import CompanyCreateForm, OfficeFormFactory
from psc.companies.models import Company


class CompanyListView(LoginRequiredMixin, ListView):
    template_name = 'companies/list.html'

    def get_queryset(self):
        return Company.objects.filter(account=self.request.user.get_account())


class CompanyAddView(LoginRequiredMixin, FormView):
    template_name = 'companies/add.html'
    form_class = CompanyCreateForm
    success_url = '/companies/'

    def get_context_data(self, **kwargs):
        context = super(CompanyAddView, self).get_context_data(**kwargs)
        context['error'] = ''
        account = self.request.user.get_account()
        company_count = Company.objects.filter(account=account).count()
        if account.is_multiple_company and company_count == settings.MAX_COMPANY_PER_ACCOUNT:
            context['error'] = "Your account has reach maximum companies ({})".format(settings.MAX_COMPANY_PER_ACCOUNT)
        elif not account.is_multiple_company and company_count == 1:
            context['error'] = "Your account can have only one company"

        if not self.request.user.is_owner():
            context['error'] = "Only owner can add company"

        instance = getattr(self, 'instance', None)

        if self.request.POST:
            context['office_form'] = OfficeFormFactory(self.request.POST, instance=instance)
        else:
            context['office_form'] = OfficeFormFactory(instance=instance)
        return context

    def get_initial(self):
        initial = super(CompanyAddView, self).get_initial()
        initial['account'] = self.request.user.get_account()
        return initial

    def form_valid(self, form):
        context = self.get_context_data()
        office_form = context['office_form']
        if office_form.is_valid():
            # Save everything after all validation passes
            self.object = form.save(user=self.request.user)
            office_form.instance = self.object
            office_form.save()
            return super(CompanyAddView, self).form_valid(form)
        else:
            # Render forms with error if any
            return self.render_to_response(self.get_context_data(form=form))


class CompanyEditView(CompanyAddView):

    def get_form_kwargs(self):
        form_kwargs = super(CompanyEditView, self).get_form_kwargs()
        form_kwargs['instance'] = get_object_or_404(
            Company, id=self.kwargs.get('pk', None), is_active=True)
        self.instance = form_kwargs['instance']
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super(CompanyEditView, self).get_context_data(**kwargs)
        context['error'] = ''
        return context


class CompanyAutocomplete(autocomplete.Select2QuerySetView):
    """View which helps to work with django-autocomplete-light
    """
    def get_queryset(self):
        """Available Products to display in autocomplete field.
        Used only in the admin panel, so it is only available for
        administrator and staff
        """
        user = self.request.user
        if not user.is_authenticated() and not user.is_staff:
            return Company.objects.none()

        qs = Company.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs
