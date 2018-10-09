import re
from django import template
from django.contrib.admin.templatetags.admin_list import result_list


def remove_tags(value):
    cleanr = re.compile('<(a|/a).*?>')
    cleantext = re.sub(cleanr, '', value)
    return cleantext


register = template.Library()
register.inclusion_tag('product/change_list.html')(result_list)
register.filter(name='removetags', filter_func=remove_tags)
