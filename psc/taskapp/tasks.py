import os
import time
from io import BytesIO

import datetime
import pytz

from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string

from psc.accounts.models import Account
from psc.activity.models import Summary, LogLine
from psc.companies.models import Company
from psc.notifications.models import Notification
from psc.core.utils import get_created_updated_objects_by_user
from psc.users.models import ActivateEmailKeys, InvitationKey
from .celery import app
from PIL import Image
from django.conf import settings
from psc.product.models import Image as ImageModel, Product
from django.core.files.uploadedfile import InMemoryUploadedFile
from psc.users.models import User
from psc.companies.models import CompanyImages
from django.db.models import Q


def crop(crop_data, size_data, file_name):
    # Method to crop image

    # Get image type from source file
    image_type = crop_data['source'].split('.')[-1]
    # Open source for cropping
    image = Image.open(os.path.join(settings.MEDIA_ROOT, crop_data['source']))

    # Crop Image by given params left top corner (x1, y1) and right bottom corner (x2, y2)
    cropped_image = image.crop((crop_data['x'],
                                crop_data['y'],
                                crop_data['width'] + crop_data['x'],
                                crop_data['height'] + crop_data['y']))

    # Resize image by given size
    resized_lg = cropped_image.resize(
        (size_data['width'], size_data['height']), Image.ANTIALIAS
    )

    # Save image to filesystem
    thumb_io = BytesIO()
    if image_type.upper() == 'JPG':
        image_type = 'jpeg'
    resized_lg.save(thumb_io, format=image_type.upper())

    thumb_file = InMemoryUploadedFile(thumb_io, None, file_name, 'image/jpeg', 0, None)
    return thumb_file


@app.task
def crop_image(crop_data, product, size_data, size_prefix, image):
    # Crop and create Image model inatance
    image_type = crop_data['source'].split('.')[-1]

    file_name = '{}{}_{}_{}.{}'.format(product.id, image.product_position, crop_data['type'], size_prefix, image_type)
    image_file = crop(crop_data, size_data, file_name)
    image.path = image_file
    image.name = image_file.name
    image.image_ready = True
    image.save()


@app.task
def crop_company_image(images, company):
    # Wait till company saving in progress
    time.sleep(1)
    # Crop Company Logo to three size
    for image_data in images:
        for key, size_data in settings.COMPANY_LOGO_SIZE.items():
            image_data['type'] = 'co'
            image_type = image_data['source'].split('.')[-1]
            image = CompanyImages.objects.create(
                name='image_in_process',
                type=image_type,
                company=company,
                crop_type=image_data['type'],
                product_position=image_data['id']
            )

            crop_image.delay(
                crop_data=image_data,
                product=company,
                size_data=size_data,
                size_prefix=key,
                image=image,
            )


@app.task
def crop_all_images(images, product):
    # Wait till product saving in progress
    time.sleep(1)
    # Crop list of images of given product
    for image_data in images:
        for type_key, sizes in settings.IMAGE_SIZES.items():
            image_data['type'] = type_key
            for key, size_data in sizes.items():
                image_type = image_data['source'].split('.')[-1]

                image = ImageModel.objects.create(
                    name='image_in_process',
                    type=image_type,
                    product=product,
                    crop_type=image_data['type'],
                    product_position=image_data['id']
                )

                crop_image.delay(
                    crop_data=image_data,
                    product=product,
                    size_data=size_data,
                    size_prefix=key,
                    image=image,
                )


@app.task
def remove_images(images_to_delete):
    # Remove images that set to delete
    for image in ImageModel.objects.filter(id__in=images_to_delete):
        ImageModel.objects.filter(product_position=image.product_position, product=image.product).delete()


@app.task
def account_summary_emails():
    # The period for which the report is to be built
    datetime_now = datetime.datetime.now(tz=pytz.UTC)
    date_from = datetime_now - settings.ACCOUNT_SUMMARY_INTERVAL
    date_to = datetime_now

    template_html = 'emails/notifications_summary.html'
    subject = u'PSC Notification Summary'
    from_email = settings.DEFAULT_FROM_EMAIL

    # Send reports to all active accounts
    for account in Account.objects.filter(is_active=True):
        user_contact_emails = account.user_contact_information.filter(
            is_active=True).values_list('email', flat=True)
        account_contact_emails = account.contactinformation_set.values_list(
            'email', flat=True)

        email_to = list(user_contact_emails) + list(account_contact_emails)

        if not email_to and account.owner.email:
            # If no additional recipient is specified
            # the report will be sent to owner account
            email_to = [account.owner.email, ]

        if email_to:
            # Get all account notifications
            notifications = Notification.objects.filter(
                Q(user__account=account) | Q(user__owner=account),
                created_at__range=[date_from, date_to]
            ).order_by('-created_at')

            if notifications:
                context = {
                    'notifications': notifications,
                }

                html_content = render_to_string(template_html, context=context)
                msg = EmailMultiAlternatives(
                    subject, html_content, from_email, email_to)
                msg.attach_alternative(html_content, "text/html")
                msg.send()


@app.task
def summary_emails():
    # Send summary email to site admin
    date = datetime.date.today()
    template_html = 'emails/summary.html'
    subject = u"PSC Summary"
    from_email = settings.DEFAULT_FROM_EMAIL
    email_to = settings.SUMMARY_EMAIL_TO

    context = {
        'product_added': [],
        'product_edited': [],
        'companies_added': [],
        'companies_edited': [],
        'users_added': [],
        'users_edited': []
    }

    for user in User.objects.all():
        # Calculate changed data using utils methods
        product_added, product_edited = get_created_updated_objects_by_user(date, user, Product)
        companies_added, companies_edited = get_created_updated_objects_by_user(date, user, Company)
        users_added, users_edited = get_created_updated_objects_by_user(date, user, User)

        # If all data is empty, the summary will not be sent
        summary_is_no_empty = product_added or product_edited or \
                              companies_added or companies_edited or \
                              users_added or users_edited

        # Check that something changes to not send empty emails
        if summary_is_no_empty:
            context['product_added'] += list(product_added)
            context['product_edited'] += list(product_edited)
            context['companies_added'] += list(companies_added)
            context['companies_edited'] += list(companies_edited)
            context['users_added'] += list(users_added)
            context['users_edited'] += list(users_edited)

    obj_count = 0
    for key, value in context.items():
        obj_count += len(value)

    if obj_count:
        html_content = render_to_string(template_html, context)

        msg = EmailMultiAlternatives(subject, html_content, from_email, email_to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()


@app.task
def create_summary_log():
    date = datetime.date.today()
    summary = Summary.objects.create()
    for user in User.objects.all():
        # Calculate changed data using utils methods
        product_added, product_edited = get_created_updated_objects_by_user(date, user, Product)
        companies_added, companies_edited = get_created_updated_objects_by_user(date, user, Company)
        users_added, users_edited = get_created_updated_objects_by_user(date, user, User)

        added = list(product_added) + list(companies_added) + list(users_added)
        edited = list(product_edited) + list(companies_edited) + list(users_edited)
        log_lines = []
        for obj in added:
            instance_type = LogLine.INSTANCE_TYPE_PRODUCT
            if isinstance(obj, Company):
                instance_type = LogLine.INSTANCE_TYPE_COMPANY
            elif isinstance(obj, User):
                instance_type = LogLine.INSTANCE_TYPE_USER
            log_lines.append(LogLine(
                summary=summary,
                user=user,
                type=LogLine.TYPE_CREATED,
                instance_type=instance_type,
                instance_name=obj.name,
                updated_at=obj.created_at,
                instance_id=obj.id
            ))

        for obj in edited:
            instance_type = LogLine.INSTANCE_TYPE_PRODUCT
            if isinstance(obj, Company):
                instance_type = LogLine.INSTANCE_TYPE_COMPANY
            elif isinstance(obj, User):
                instance_type = LogLine.INSTANCE_TYPE_USER
            log_lines.append(LogLine(
                summary=summary,
                user=user,
                type=LogLine.TYPE_EDITED,
                instance_type=instance_type,
                instance_name=obj.name,
                updated_at=obj.edited_at,
                instance_id=obj.id
            ))
        LogLine.objects.bulk_create(log_lines)

    if not Summary.objects.get(id=summary.id).logline_set.all():
        Summary.objects.filter(id=summary.id).delete()

@app.task
def send_activation_email(protocol, domain, key, email_to):
    # Send Email with activation code
    template_html = 'emails/activate.html'
    subject = u"PSC Account Activation"
    from_email = settings.DEFAULT_FROM_EMAIL

    context = {
        'key': key,
        'protocol': protocol,
        'domain': domain
    }
    html_content = render_to_string(template_html, context)

    msg = EmailMultiAlternatives(subject, html_content, from_email, [email_to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@app.task
def send_invitation_email(protocol, domain, key, email_to):
    # Send Email with invitation link
    template_html = 'emails/invite.html'
    subject = u"PSC Account Invitaion"
    from_email = settings.DEFAULT_FROM_EMAIL

    context = {
        'key': key,
        'protocol': protocol,
        'domain': domain
    }
    html_content = render_to_string(template_html, context)

    msg = EmailMultiAlternatives(subject, html_content, from_email, [email_to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@app.task
def expire_keys():
    # Task to remove expired activations keys
    date = datetime.date.today() - datetime.timedelta(days=settings.ACTIVATION_KEY_EXPIRE_DAYS)
    ActivateEmailKeys.objects.filter(created_at=date).delete()


@app.task
def delete_not_activated_users():
    # Task to delete not activated users
    date = datetime.date.today() - datetime.timedelta(days=settings.ACTIVATION_USER_EXPIRE_DAYS)
    User.objects.filter(date_joined__contains=date, is_active=False).delete()


@app.task
def remove_inactive_accounts():
    # Task to delete not active account with all data
    date = datetime.date.today() - datetime.timedelta(days=settings.INACTIVE_ACCOUNT_DELETE_AFTER_DAYS)
    accounts = Account.objects.filter(deleted_at__contains=date, is_active=False)
    # Delete owners first
    owner_ids = []
    for account in accounts:
        owner_ids.append(account.owner.id)
    User.objects.filter(id__in=owner_ids).delete()
    # Delete Accounts with all data
    Account.objects.filter(deleted_at__contains=date, is_active=False).delete()


@app.task
def expire_inactive_users():
    # Task to delete not confirmed users and not accepted invations
    date = datetime.date.today() - datetime.timedelta(days=settings.INVITED_USER_EXPIRE_DAYS)
    # Delete not confirmed users first
    User.objects.filter(created_at__contains=date, confirmed=False).delete()
    # Delete not accepted invitations
    InvitationKey.objects.filter(created_at__contains=date).delete()


@app.task
def expire_notifications():
    # Task to delete not confirmed users and not accepted invations
    date = datetime.date.today() - datetime.timedelta(days=settings.INVITED_USER_EXPIRE_DAYS)
    # Delete expired notifications
    Notification.objects.filter(created_at__contains=date, status=Notification.STATUS_ARCHIVED).delete()
