from django.db import models
from django.db.models.signals import post_delete, post_save, pre_delete

from psc.companies.models import Company
from psc.core.models import ImageBaseModel
from psc.notifications.models import Notification
from psc.product.utils import get_document_upload_path
from psc.users.models import User
from psc.core.models import ImageBaseModel


class Product(models.Model):
    name = models.CharField(max_length=255)
    short_description = models.CharField(max_length=150)
    description = models.TextField()
    company = models.ForeignKey(Company)
    category = models.ManyToManyField('Category')

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, blank=True, null=True, related_name='product_created_by')

    edited_at = models.DateTimeField(auto_now=True)
    edited_by = models.ForeignKey(User, blank=True, null=True, related_name='product_edited_by')
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    __original_approved = None

    def __init__(self, *args, **kwargs):
        super(Product, self).__init__(*args, **kwargs)
        self.__original_approved = self.is_approved

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        if self.company.is_active is False:
            self.is_active = False

        super(Product, self).save(*args, **kwargs)

        # get user who changed or create product
        user = self.edited_by \
            if self.edited_by and self.created_by != self.edited_by \
            else self.created_by

        if self.is_approved != self.__original_approved and user:
            notification_type = Notification.TYPE_PRODUCT_APPROVED \
                if self.is_approved else Notification.TYPE_PRODUCT_DENY

            # create notification  when product is approved or deny
            Notification.objects.create(
                user=user,
                type=notification_type,
                instance_name=self.name
            )
            self.__original_approved = self.is_approved


class Documentation(models.Model):

    TYPE_DOC = 'doc'
    TYPE_DOCX = 'docx'
    TYPE_PDF = 'pdf'
    TYPE_CSV = 'csv'
    TYPE_XLS = 'xls'
    TYPE_XLSX = 'xlsx'
    TYPE_ODF = 'odf'
    TYPE_ODT = 'odt'

    TYPE_CHOICES = (
        (TYPE_DOC, TYPE_DOC),
        (TYPE_DOCX, TYPE_DOCX),
        (TYPE_PDF, TYPE_PDF),
        (TYPE_CSV, TYPE_CSV),
        (TYPE_XLS, TYPE_XLS),
        (TYPE_XLSX, TYPE_XLSX),
        (TYPE_ODF, TYPE_ODF),
        (TYPE_ODT, TYPE_ODT)
    )

    name = models.CharField(max_length=150)
    path = models.FileField(upload_to=get_document_upload_path)
    type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    product = models.ForeignKey(Product)

    def __str__(self):
        return self.name

    def available_file_types(self):
        # Calculate and return available docs extensions
        return [x[1] for x in self.TYPE_CHOICES]

    def save(self, *args, **kwargs):
        # Set image type before save instance
        self.type = self.path.name.split('.')[1]
        return super(Documentation, self).save(*args, **kwargs)


class Image(ImageBaseModel):
    product = models.ForeignKey(Product, blank=True, null=True)


class Video(models.Model):
    name = models.CharField(max_length=255)
    user_path = models.URLField()
    ph_path = models.URLField(blank=True, null=True)
    product = models.ForeignKey(Product)

    def get_video_url(self):
        # Return video URL by priority, ph_path have graitest priority
        return self.ph_path or self.user_path

    def __str__(self):
        return self.name

    @staticmethod
    def get_video_code(url):
        # Calculate and return video URL type (youtube or vimeo) and video code
        link_type = None
        video_id = None
        if 'youtube' in url or 'youtu.be' in url:
            if '.be' in url:
                video_id = url.split('/')[-1]
            else:
                video_id = url.split('=')[-1]
            link_type = 'youtube'
        elif 'vimeo' in url:
            video_id = url.split('/')[-1]
            link_type = 'vimeo'
        return link_type, video_id


class Category(models.Model):
    name = models.CharField(max_length=255)
    url = models.SlugField(max_length=255)
    description = models.TextField()
    parent = models.ForeignKey('Category', blank=True, null=True)

    def get_children(self):
        return Category.objects.filter(parent__id=self.id)

    def get_parents_list(self):
        return Category.objects.filter(parent__id=self.parent.id)

    def __str__(self):
        return self.name


def post_delete_handler(sender, instance, **kwargs):
    # Handler to post delete to delete same instances from second database
    sender.objects.using('duplicate').filter(id=instance.id).delete()


def post_delete_product(sender, instance, **kwargs):
    try:
        # create notification when product is removed
        Notification.objects.create(
            user=instance.company.account.owner,
            type=Notification.TYPE_PRODUCT_REMOVED,
            instance_name=instance.name
        )
    except:
        pass

    post_delete_handler(sender, instance, **kwargs)


def post_create_handler(sender, instance, **kwargs):
    # Handler to save same instance to second database
    instance_data = {}
    for key, value in instance.__dict__.items():
        if not key.startswith('_'):
            instance_data[key] = value
    try:
        updated = sender.objects.using('duplicate').filter(id=instance.id).update(**instance_data)
        if not updated:
            sender.objects.using('duplicate').create(**instance_data)
    except:
        pass


def set_images_edited_outside(sender, instance, **kwargs):
    try:
        sender.objects.filter(
            product=instance.product,
            product_position=instance.product_position
        ).update(is_edited_outside=True)
    except Product.DoesNotExist:
        pass


def image_delete(sender, instance, **kwargs):
    try:
        instance.path.delete(False)
    except IOError:
        pass


pre_delete.connect(image_delete, Image)
post_delete.connect(set_images_edited_outside, Image)

post_delete.connect(post_delete_handler, Image)
post_delete.connect(post_delete_handler, Documentation)
post_delete.connect(post_delete_handler, Video)
post_delete.connect(post_delete_product, Product) # different method

post_save.connect(post_create_handler, Image)
post_save.connect(post_create_handler, Product)
post_save.connect(post_create_handler, Documentation)
post_save.connect(post_create_handler, Video)
