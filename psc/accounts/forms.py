from django import forms
from django.forms.models import inlineformset_factory

from psc.accounts.models import Account, ContactInformation
from psc.users.models import User

ContactInformationFactory = inlineformset_factory(
    Account,
    ContactInformation,
    extra=1,
    can_delete=True,
    fields=('contact_name', 'email')
)


class AccountForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account', None)
        super(AccountForm, self).__init__(*args, **kwargs)
        self.fields['owner'].widget = forms.HiddenInput()
        if self.account:
            users_ids = list(self.account.user_set.all().values_list('id', flat=True)) + [self.account.owner.id]
            self.fields['user_contact_information'].queryset = User.objects.filter(id__in=users_ids)

    class Meta:
        model = Account
        exclude = ('is_multiple_company', 'is_multiple_users', 'is_active', 'deleted_at')
