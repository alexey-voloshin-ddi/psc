from django import forms
from django.template.loader import get_template
from django.template import Context
from django.conf import settings


class ImageCropWidget(forms.Widget):

    def __init__(self, images_queryset=None, is_single=False, is_company=False, *args, **kwargs):
        # Override init method to set required data for widget
        self.images = images_queryset
        self.is_single = is_single
        self.is_company = is_company
        super(ImageCropWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        # Set render widget logic
        template = get_template('widgets/crop_widget.html')
        context = Context({'name': name, 'value': value, 'sizes': settings.IMAGE_SIZES, 'images': self.images,
                           "MEDIA_URL": settings.MEDIA_URL, 'is_single': self.is_single, 'is_company': self.is_company})
        return template.render(context)


class VideoWidget(forms.Widget):

    def __init__(self, videos_queryset=None, *args, **kwargs):
        self.videos = videos_queryset
        super(VideoWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        template = get_template('widgets/video_widget.html')
        context = Context({'name': name, 'value': value, 'sizes': settings.IMAGE_SIZES, 'videos': self.videos})
        return template.render(context)


class CategoryWidget(forms.Widget):

    def __init__(self, categories=None, *args, **kwargs):
        self.categories = categories
        super(CategoryWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        template = get_template('widgets/category_widget.html')
        context = Context({'name': name,
                           'value': value,
                           'categories': self.categories,
                           'max_cat_count': settings.MAX_CATEGORY_COUNT})
        return template.render(context)
