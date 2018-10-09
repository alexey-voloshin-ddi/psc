from django.db import models
from psc.product.utils import get_images_upload_path


class ImageBaseModel(models.Model):
    TYPE_PNG = 'png'
    TYPE_JPEG = 'jpeg'
    TYPE_GIF = 'gif'

    TYPE_CHOICES = (
        (TYPE_PNG, TYPE_PNG),
        (TYPE_JPEG, TYPE_JPEG),
        (TYPE_GIF, TYPE_GIF),
    )

    CROP_TYPE_THUMBNAIL = 'th'
    CROP_TYPE_LISTING = 'pl'
    CROP_TYPE_PRODUCT = 'pr'
    CROP_TYPE_COMPANY = 'co'

    CROP_TYPE_CHOICES = (
        (CROP_TYPE_THUMBNAIL, 'Thumbnail'),
        (CROP_TYPE_LISTING, 'Product Listing'),
        (CROP_TYPE_PRODUCT, 'Product Detail'),
        (CROP_TYPE_COMPANY, 'Company Logo')
    )

    name = models.CharField(max_length=150)
    type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    crop_type = models.CharField(max_length=2, choices=CROP_TYPE_CHOICES)
    path = models.ImageField(upload_to=get_images_upload_path, blank=True, null=True)
    image_ready = models.BooleanField(default=False)
    product_position = models.IntegerField()
    is_edited_outside = models.BooleanField(default=False)

    class Meta:
        abstract = True

    __original_path = None

    def get_image_size_prefix(self):
        # Calculate and return image size prefix
        size_prefix = 'lg'
        if 'md' in self.path.name:
            size_prefix = 'md'
        elif 'sm' in self.path.name:
            size_prefix = 'sm'
        return size_prefix

    def __init__(self, *args, **kwargs):
        super(ImageBaseModel, self).__init__(*args, **kwargs)
        self.__original_path = self.path

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_edit = False
        if self.pk:
            is_edit = True

        super(ImageBaseModel, self).save(*args, **kwargs)

        if is_edit and self.__original_path and self.__original_path != self.path:
            # mark images as is_edited_outside

            if hasattr(self, 'product'):
                self._meta.model.objects.filter(
                    product=self.product,
                    product_position=self.product_position
                ).update(is_edited_outside=True)

            elif hasattr(self, 'company'):
                self._meta.model.objects.filter(
                    company=self.company,
                    product_position=self.product_position
                ).update(is_edited_outside=True)
