from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic.base import View
from django.views.generic.edit import FormView
from django.contrib import messages

from psc.accounts.forms import AccountForm, ContactInformationFactory
from psc.taskapp.tasks import (
    account_summary_emails, create_summary_log, summary_emails
)


class AccountSettings(LoginRequiredMixin, FormView):
    template_name = 'account/settings.html'
    form_class = AccountForm
    success_url = '/account/'

    def get_context_data(self, **kwargs):
        context = super(AccountSettings, self).get_context_data(**kwargs)
        instance = self.request.user.get_account()
        if self.request.POST:
            context['contact_information_form'] = ContactInformationFactory(self.request.POST, instance=instance)
        else:
            context['contact_information_form'] = ContactInformationFactory(instance=instance)
        return context

    def get_form_kwargs(self):
        form_kwargs = super(AccountSettings, self).get_form_kwargs()
        form_kwargs['instance'] = self.request.user.get_account()
        form_kwargs['account'] = form_kwargs['instance']
        return form_kwargs

    def form_valid(self, form):
        context = self.get_context_data()
        office_form = context['contact_information_form']
        if office_form.is_valid():
            # Save everything after all validation passes
            self.object = form.save()
            office_form.instance = self.object
            office_form.save()

            message_success = 'Information was saved successfully.'
            messages.success(self.request, message_success)

            return super(AccountSettings, self).form_valid(form)
        else:
            # Render forms with error if any
            return self.render_to_response(self.get_context_data(form=form))


class TestOwnerEmail(View):

    def get(self, request):
        account_summary_emails()
        return redirect('/account/')


class TestSummaryLog(View):

    def get(self, request):
        create_summary_log.delay()
        return redirect('/account/')

class TestSummaryEmail(View):

    def get(self, request):
        summary_emails.delay()
        return redirect('/account/')
