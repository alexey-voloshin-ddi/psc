import datetime

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query_utils import Q
from django.shortcuts import redirect, get_object_or_404
from django.urls.base import reverse
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView, CreateView
from django.views.generic.list import ListView

from psc.taskapp.tasks import send_invitation_email
from psc.users.forms import RegistrationForm, ResendActivationLink, InviteForm
from psc.users.models import ActivateEmailKeys, InvitationKey


class UsersList(LoginRequiredMixin, ListView):
    template_name = 'users/list.html'

    def get_context_data(self, **kwargs):
        context = super(UsersList, self).get_context_data(**kwargs)
        context['invitation_list'] = InvitationKey.objects.filter(
            user=self.request.user)
        return context

    def get_queryset(self):
        return self.request.user.get_account().user_set.all()


class InviteUserView(LoginRequiredMixin, CreateView):
    template_name = 'users/invite.html'
    form_class = InviteForm

    def get_success_url(self):
        return reverse('users:user-list')

    def get_context_data(self, **kwargs):
        context = super(InviteUserView, self).get_context_data(**kwargs)
        context['error'] = ''
        account = self.request.user.get_account()
        users_count = account.user_set.all().count()
        invites_count = InvitationKey.objects.filter(
            Q(user__account=account) |
            Q(user__owner=account)
        ).distinct().count()
        all_count = users_count + invites_count
        if account.is_multiple_users and all_count >= \
            settings.MAX_USER_PER_ACCOUNT:
            context['error'] = "You can't invite more users, account " \
                               "reach max users and invitations."
        elif not account.is_multiple_users and all_count == 0:
            context['error'] = "You can't invite more users, " \
                               "account can have only one user."
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.get_account(),
            'domain': self.request.META['HTTP_HOST'],
            'protocol': 'https' if self.request.is_secure() else 'http',
            'user': self.request.user
        })
        return kwargs


class ActivateUserView(TemplateView):
    template_name = 'users/activation.html'

    def get(self, request, *args, **kwargs):
        # Method to activate user when user come from link in email

        # Get key from url kwargs
        key = kwargs.get('key', None)

        context = self.get_context_data()

        try:
            # Try to find user to activate by key
            user = ActivateEmailKeys.objects.get(key=key).user
            # Set user as active
            user.is_active = True
            # Save User
            user.save()
            # Remove activation key from database
            ActivateEmailKeys.objects.filter(key=key).delete()

        except ActivateEmailKeys.DoesNotExist:
            # Set context error to show it user if user fro activation was not found
            context['error'] = True

        return self.render_to_response(context)


class RegistrationView(CreateView):
    template_name = 'users/registration.html'
    form_class = RegistrationForm
    invitation = None
    success_url = '/users/registration/done/'

    def get_context_data(self, **kwargs):
        context = super(RegistrationView, self).get_context_data(**kwargs)
        if 'key' in self.kwargs and not self.invitation:
            context['error'] = True
        return context

    def get_invitation(self):
        if not self.invitation:
            if 'key' in self.kwargs:
                try:
                    self.invitation = InvitationKey.objects.get(
                        key=self.kwargs['key'])
                except InvitationKey.DoesNotExist:
                    self.invitation = None
        return self.invitation

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'invitation_key': self.kwargs.get('key'),
            'domain': self.request.META['HTTP_HOST'],
            'protocol': 'https' if self.request.is_secure() else 'http'
        })
        return kwargs

    def get_initial(self):
        invitation = self.get_invitation()
        initial = super(RegistrationView, self).get_initial()
        if invitation:
            initial['email'] = self.invitation.email
        return initial


class ReSendActivationKey(FormView):
    template_name = 'users/resend_activation.html'
    form_class = ResendActivationLink

    def form_valid(self, form):
        form.save(request=self.request)
        return redirect('/users/resend/activation/done/')


class ResendInvitation(View):

    def get(self, request, pk):
        instance = get_object_or_404(InvitationKey, pk=pk)

        invite_key = InvitationKey.objects.create(
            email=instance.email,
            user=instance.user,
            created_at=datetime.date.today(),
            access_level=instance.access_level
        )

        InvitationKey.objects.filter(id=pk).delete()

        protocol = 'https' if request.is_secure() else 'http'
        domain = request.META['HTTP_HOST']

        send_invitation_email(
            protocol, domain, invite_key.key, invite_key.email)

        url = reverse('admin:users_invitationkey_change', args=[invite_key.id])
        return redirect(url)
