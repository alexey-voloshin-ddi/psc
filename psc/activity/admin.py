from django.contrib import admin

# Register your models here.
from psc.activity.models import LogLine, Summary


class LogInline(admin.TabularInline):
    model = LogLine
    readonly_fields = ('user', 'type', 'instance_type', 'instance_name', 'updated_at', 'link')
    exclude = ('instance_id', )

    def has_add_permission(self, request):
        return False

    def link(self, obj):
        if obj.instance_id:
            url = '/admin/'
            text = 'Go to'
            if obj.instance_type == LogLine.INSTANCE_TYPE_PRODUCT:
                url += 'product/product/'
                text += " Product"
            elif obj.instance_type == LogLine.INSTANCE_TYPE_COMPANY:
                url += 'companies/company/'
                text += " Company"
            else:
                url += 'users/user/'
                text += " User"

            url += "{}/".format(obj.instance_id)
            return "<a target='_blank' href='{}'>{}</a>".format(url, text)
        return 'Old log have no link'
    link.allow_tags = True


class SummaryAdmin(admin.ModelAdmin):
    inlines = [LogInline]
    readonly_fields = ('created_at', )

    def has_add_permission(self, request):
        return False

admin.site.register(Summary, SummaryAdmin)
