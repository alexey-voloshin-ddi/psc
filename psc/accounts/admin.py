from django.contrib import admin

# Register your models here.
from psc.accounts.models import Account, ContactInformation
from psc.users.models import User


class ContactInformationInline(admin.TabularInline):
    model = ContactInformation
    extra = 1


class AccountAdmin(admin.ModelAdmin):
    inlines = (ContactInformationInline, )

    def get_form(self, request, obj=None, **kwargs):
        # Override method to set available companies by user from bequest
        form = super(AccountAdmin, self).get_form(request, **kwargs)
        if obj:
            users_ids = list(obj.user_set.all().values_list('id', flat=True)) + [obj.owner.id]
            form.base_fields['user_contact_information'].queryset = User.objects.filter(id__in=users_ids)

        return form

admin.site.register(Account, AccountAdmin)
