import json
import re
import magic
import os
from django import forms
from django.forms.models import inlineformset_factory
from dal import autocomplete

from psc.companies.models import Company
from psc.product.models import Product, Documentation, Video, Image, Category
from psc.product.widgets import ImageCropWidget, CategoryWidget
from psc.taskapp.tasks import crop, remove_images, crop_all_images
from django.conf import settings
from django.utils.crypto import get_random_string


class DocumentationAdminForm(forms.ModelForm):

    class Meta:
        model = Documentation
        fields = "__all__"
        widgets = {
            'product': autocomplete.ModelSelect2(url='product:autocomplete')
        }

    def clean_path(self):

        # Check that file has right extension
        doc_format = self.cleaned_data['path'].name.split('.')[-1]
        if doc_format not in Documentation().available_file_types():
            raise forms.ValidationError('Unsupported file format.')

        # Check that file has right mime type
        file = self.cleaned_data['path']
        file_type = magic.from_buffer(file.read(), mime=True)
        file.seek(0)
        if file_type not in settings.VALID_MIME_TYPES:
            raise forms.ValidationError('Unsupported file format.')

        return self.cleaned_data['path']


class DocumentationForm(DocumentationAdminForm):
    name = forms.CharField(required=False)

    class Meta:
        model = Documentation
        fields = ('path', )

    def save(self, commit=True):
        document = super(DocumentationForm, self).save(commit)
        name = self.cleaned_data.get('name')
        # Check that name is provided
        if not name:
            # Generate name if not provided
            name = os.path.basename(self.cleaned_data['path'].name)
            if Documentation.objects.filter(name=name).exists():
                name += get_random_string(5)

        document.name = name
        document.save()
        return document


class VideoAdminForm(forms.ModelForm):
    name = forms.CharField(required=False)

    class Meta:
        model = Video
        fields = ('name', 'user_path')
        widgets = {
            'product': autocomplete.ModelSelect2(url='product:autocomplete')
        }

    def clean_user_path(self):
        user_path = self.cleaned_data['user_path']

        is_valid_url = re.match(settings.VIDEO_VALIDATION_REGEXP, user_path)
        # Check that video url belong to Youtube or Vimeo
        if not is_valid_url:
            raise forms.ValidationError('Only youtube or vimeo videos is available.')
        return user_path

    def clean_ph_path(self):
        ph_path = self.cleaned_data.get('ph_path')
        if ph_path:
            is_valid_url = re.match(settings.VIDEO_VALIDATION_REGEXP, ph_path)
            # Check that video url belong to Youtube or Vimeo
            if not is_valid_url:
                raise forms.ValidationError('Only youtube or vimeo videos is available.')
        return ph_path

    def save(self, commit=True):
        video = super(VideoAdminForm, self).save(commit)
        name = self.cleaned_data.get('name')
        # Check that name is provided
        if not name:
            # Generate name if not provided
            name = Video.get_video_code(video.get_video_url())[1]
            if Video.objects.filter(name=name).exists():
                name += get_random_string(5)
        video.name = name
        video.save()
        return video


class VideoForm(VideoAdminForm):

    class Meta:
        model = Video
        fields = "__all__"


class ImageAdminForm(forms.ModelForm):
    SIZE_CHOICES = (
        (None, '----'),
        ('lg', 'lg'),
        ('md', 'md'),
        ('sm', 'sm'),
    )

    size = forms.CharField(widget=forms.Select(choices=SIZE_CHOICES))
    image = forms.CharField(widget=ImageCropWidget(is_single=True), required=False)

    class Meta:
        model = Image
        fields = ("image", "crop_type", "product")
        widgets = {
            'product': autocomplete.ModelSelect2(url='product:autocomplete')
        }

    def __init__(self, *args, **kwargs):
        super(ImageAdminForm, self).__init__(*args, **kwargs)
        # Check is update
        if self.instance.pk:
            # Set instance image to cropper widget
            images = [self.instance]
            self.fields['image'].widget = ImageCropWidget(images_queryset=images, is_single=True)
            # Hide size input
            self.fields['size'].widget = forms.HiddenInput()
            self.fields['size'].required = False

    def clean_image(self):
        # Validate that image was provided and have crop data
        data = self.cleaned_data['image']
        images_data = []
        if data:
            try:
                images_data = json.loads(data)
            except ValueError:
                raise forms.ValidationError('Wrong json format')

            if not images_data:
                raise forms.ValidationError('At least one Crop is required')

        return images_data

    def save(self, commit=True):
        image = super(ImageAdminForm, self).save(commit=False)
        # Check is images was provided, can be not provided on update
        if self.cleaned_data['image']:
            # Collect data for crop new image
            image_data = self.cleaned_data['image'][0]
            image.product_position = image_data['id']
            image.save()

            try:
                size = image.get_image_size_prefix()
            except TypeError:
                size = self.cleaned_data['size']

            if image.crop_type:
                size_data = settings.COMPANY_LOGO_SIZE[size]
            else:
                size_data = settings.IMAGE_SIZES[image.crop_type][size]

            if not image.name:
                image_type = image_data['source'].split('.')[-1]
                file_name = '{}{}_{}_{}.{}'.format(image.id, image.product_position, image.crop_type, size, image_type)
                image.name = file_name

            # Crop and save image
            image_file = crop(image_data, size_data, image.name)
            image.path = image_file
            image.image_ready = True
            image.save()

        return image


DocumentationFormFactory = inlineformset_factory(
    Product,
    Documentation,
    form=DocumentationForm,
    extra=1,
    fields=('name', 'path'),
    can_delete=False
)

VideoFormFactory = inlineformset_factory(
    Product,
    Video,
    form=VideoForm,
    extra=1,
    fields=('name', 'user_path', 'ph_path'),
    can_delete=False
)


class ProductCreateAdminForm(forms.ModelForm):
    images_to_delete = forms.CharField(widget=forms.HiddenInput, required=False)
    images = forms.CharField(widget=ImageCropWidget, required=False)
    # category = forms.CharField(widget=CategoryWidget)

    def __init__(self, *args, **kwargs):
        # Store user instance inside form for letter use
        self.user = kwargs.pop('user', None)
        super(ProductCreateAdminForm, self).__init__(*args, **kwargs)
        # Check is update
        if self.instance.pk:
            # Send images to cropper widget
            images = Image.objects.filter(product=self.instance, path__contains='lg', crop_type=Image.CROP_TYPE_PRODUCT)
            # Check is images edited outside
            if Image.objects.filter(product=self.instance, is_edited_outside=True).exists():
                positions = Image.objects.filter(product=self.instance).values_list('product_position', flat=True)
                # Check that all cover (lg_pr) exists
                if positions != images.count:
                    images_positions = images.values_list('product_position', flat=True)
                    # Convert queryset to list for append fake images with default cover
                    images = list(images)
                    # Finding what images are missing
                    difference = list(set(positions) - set(images_positions))
                    for position in difference:
                        # Create Fake Image Cover to show it
                        images.append({
                            'id': Image.objects.filter(product_position=position, product=self.instance).first().id,
                            'is_edited_outside': True,
                            'is_fake': True,
                            'product_position': position
                        })

            self.fields['images'].widget = ImageCropWidget(images_queryset=images)
        if self.user:
            # Set available companies by given user
            account = self.user.get_account()
            self.fields['company'].queryset = Company.objects.filter(
                account=account, is_active=True)
            self.fields['is_approved'].widget = forms.HiddenInput()

        # self.fields['category'].widget = CategoryWidget(categories=Category.objects.filter(parent__isnull=True))

    class Meta:
        model = Product
        fields = '__all__'
        exclude = ('created_by', 'edited_by', 'category', 'is_active')

    def clean(self):
        # Validate inline models before save to not allow save product before documents and videos
        instance = self.instance if self.instance.id else None

        videos_formset_data = VideoFormFactory(self.data, instance=instance)
        documents_formset_data = DocumentationFormFactory(self.data, self.files, instance=instance)

        if not videos_formset_data.is_valid():
            raise forms.ValidationError('One of video not valid')

        if not documents_formset_data.is_valid():
            raise forms.ValidationError('One of documents not valid')

    def clean_category(self):
        category_data = self.cleaned_data['category']
        if category_data:
            try:
                category_data = json.loads(category_data)
            except ValueError:
                category_data = []

        category_ids = [value for key, value in category_data.items()]
        return Category.objects.filter(id__in=category_ids)

    def clean_images(self):
        data = self.cleaned_data['images']
        images_data = []
        at_least_one_error = 'At least one Crop is required'

        # Check that data is provided
        if data:
            # Validate data format
            try:
                images_data = json.loads(data)
            except ValueError:
                images_data = []

            if not images_data:
                raise forms.ValidationError(at_least_one_error)

        # If data not provided and it's update
        elif self.instance.pk:
            # Check that previous images exists
            images_count = self.instance.image_set.all().count()
            if not images_count:
                raise forms.ValidationError(at_least_one_error)
            # Check that previous images was not set to delete
            elif self.cleaned_data['images_to_delete']:
                collected_ids = []
                for image in Image.objects.filter(id__in=self.cleaned_data['images_to_delete']):
                    collected_ids += Image.objects.filter(
                        product=image.product,
                        crop_type=image.crop_type
                    ).values_list('id', flat=True)
                if not self.instance.image_set.all().exclude(id__in=collected_ids):
                    raise forms.ValidationError(at_least_one_error)

        elif not self.instance.pk:
            raise forms.ValidationError(at_least_one_error)

        return images_data

    def clean_images_to_delete(self):
        data = self.cleaned_data['images_to_delete']
        # Check that images set to delete have currect format
        if data:
            try:
                data = json.loads(data)
            except ValueError:
                raise forms.ValidationError('Wrong json format')
        return data

    def save(self, commit=True, user=None):
        if self.instance.pk:
            self.instance.category.clear()

        product = super(ProductCreateAdminForm, self).save(commit)
        if user and not product.created_by:
            product.created_by = user
        else:
            product.edited_by = user
        product.save()

        if self.cleaned_data['images_to_delete']:
            # Send Celery task to delete images that was set to delete
            remove_images.delay(self.cleaned_data['images_to_delete'])

        # Send Celery task to crop all images
        crop_all_images.delay(self.cleaned_data['images'], product)

        return product
