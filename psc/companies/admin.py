from django.contrib import admin
from django.conf import settings

from psc.companies.forms import CompanyAdminForm
from psc.companies.models import Company, Office, CompanyImages
from psc.companies.forms import CompanyImageForm

class OfficeInline(admin.TabularInline):
    model = Office
    extra = 1


class CompanyAdmin(admin.ModelAdmin):
    form = CompanyAdminForm
    readonly_fields = ('created_by', 'edited_by', 'is_active')
    # inlines = (OfficeInline, )

    def save_model(self, request, obj, form, change):
        # Override method to set approved/not approved flag based on user that make changes in admin interface
        if not change:
            obj.created_by = request.user
        else:
            obj.edited_by = request.user

        obj.save()


class CompanyImageAdmin(admin.ModelAdmin):
    form = CompanyImageForm
    exclude = ('type', )
    list_display = ('name', 'image_preview', 'crop_type', 'image_size',
                    'company', 'image_ready')
    change_list_template = 'product/images_list.html'

    def get_readonly_fields(self, request, obj=None):
        # Override method that set readonly fields in update view
        if obj:
            return ['company', 'crop_type', 'image_size', 'is_edited_outside']
        else:
            return []

    def image_size(self, obj):
        # Show image size for admin list display
        return obj.get_image_size_prefix()

    def image_preview(self, obj):
        # Create image preview frame
        return "<img src='{}{}' height='50px' width='50px'>".format(settings.MEDIA_URL, obj.path)
    image_preview.allow_tags = True


admin.site.register(CompanyImages, CompanyImageAdmin)
admin.site.register(Company, CompanyAdmin)
