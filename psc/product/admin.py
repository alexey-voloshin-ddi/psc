from django.contrib import admin
from django.conf import settings
from django.forms.widgets import CheckboxInput

from psc.accounts.models import Account
from psc.companies.models import Company
from psc.product.forms import (
    ProductCreateAdminForm, DocumentationForm, DocumentationAdminForm,
    VideoAdminForm, ImageAdminForm, VideoForm)
from psc.product.models import Product, Image, Documentation, Video, Category


class DocumentInline(admin.TabularInline):
    model = Documentation
    form = DocumentationForm
    fields = ('name', 'path')
    extra = 1


class VideoInline(admin.TabularInline):
    model = Video
    form = VideoForm
    extra = 1
    fields = ('name', 'video_preview', 'user_path', 'ph_path')
    readonly_fields = ('video_preview', )

    def video_preview(self, instance):
        # Create video preview frame
        url = instance.get_video_url()
        video_type, video_id = instance.__class__.get_video_code(url)

        if video_type == 'youtube':
            # Create frame if it's youtube video
            return '<iframe width="360" height="360" src="https://www.youtube.com/embed/{}" frameborder="0" ' \
                   'webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>'.format(video_id)
        elif video_type == 'vimeo':
            # Create frame if it's vimeo video
            return '<iframe src="https://player.vimeo.com/video/{}" width="360" height="360" frameborder="0" ' \
                   'webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>'.format(video_id)
        return ""
    video_preview.allow_tags = True


class ProductAdmin(admin.ModelAdmin):
    form = ProductCreateAdminForm
    inlines = (DocumentInline, VideoInline)
    list_display = ('name', 'company', 'created_at', 'edited_at',
                    'is_approved', 'is_active')
    list_filter = ('is_approved', 'is_active', 'created_at', 'edited_at')
    readonly_fields = ('created_by', 'edited_by', 'is_active')

    class Meta:
        model = Product

    def get_form(self, request, obj=None, **kwargs):
        # Override method to set available companies by user from bequest
        form = super(ProductAdmin, self).get_form(request, **kwargs)
        account = request.user.get_account()
        if obj:
            account = obj.created_by.get_account()
        form.base_fields['company'].queryset = Company.objects.filter(account=account)

        form.base_fields['is_approved'].widget = CheckboxInput()
        form.base_fields['is_approved'].required = False

        return form

    def save_model(self, request, obj, form, change):
        # Set approved/ not approved flag based on user type that make changes in admin interface
        if not change:
            obj.created_by = request.user
        else:
            obj.edited_by = request.user

        obj.save()


class DocumentationAdmin(admin.ModelAdmin):
    form = DocumentationAdminForm
    readonly_fields = ('type', )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('product',)
        return self.readonly_fields


class VideoAdmin(admin.ModelAdmin):
    form = VideoAdminForm
    fields = ('name', 'product', 'user_path', 'ph_path')
    list_display = ('name', 'product')
    search_fields = ('name', 'product__name', 'ph_path')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('product',)
        return self.readonly_fields


class ImageAdmin(admin.ModelAdmin):
    form = ImageAdminForm
    exclude = ('type', )
    list_display = ('name', 'image_preview', 'crop_type', 'image_size',
                    'product', 'image_ready')
    change_list_template = 'product/images_list.html'

    def get_readonly_fields(self, request, obj=None):
        # Override method that set readonly fields in update view
        if obj:
            return ['product', 'crop_type', 'image_size', 'is_edited_outside']
        else:
            return []

    def image_size(self, obj):
        # Show image size for admin list display
        return obj.get_image_size_prefix()

    def image_preview(self, obj):
        # Create image preview frame
        return "<img src='{}{}' height='50px' width='50px'>".format(
            settings.MEDIA_URL, obj.path)
    image_preview.allow_tags = True


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'url': ('name',)}


admin.site.register(Product, ProductAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Documentation, DocumentationAdmin)
admin.site.register(Video, VideoAdmin)
# admin.site.register(Category, CategoryAdmin)
