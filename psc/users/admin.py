from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

from psc.users.forms import MyUserChangeForm, MyUserCreationForm
from psc.users.models import InvitationKey
from .models import User


class UserAdmin(AuthUserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    fieldsets = (
                    ('User Profile', {'fields': (
                    'name', 'account', 'is_approved', 'phone', 'access_level',
                    'confirmed')}),
                ) + AuthUserAdmin.fieldsets
    list_display = ('username', 'name', 'is_superuser')
    search_fields = ['name']
    readonly_fields = ('created_by', 'edited_by')

    def save_model(self, request, obj, form, change):
        # Override method to set approved/not approved flag based on user that make changes in admin interface
        if change:
            obj.created_by = request.user
        else:
            obj.edited_by = request.user

        obj.save()


@admin.register(InvitationKey)
class InvitationKeyAdmin(admin.ModelAdmin):
    pass

admin.site.register(User, UserAdmin)
