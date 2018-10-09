import json
from django import forms
from django.conf import settings
from django.forms.models import inlineformset_factory
from dal import autocomplete

from psc.accounts.models import Account
from psc.companies.models import Company, Office, CompanyImages
from psc.product.models import Image
from psc.product.widgets import ImageCropWidget
from psc.taskapp.tasks import remove_images, crop_company_image
from psc.product.forms import ImageAdminForm


OfficeFormFactory = inlineformset_factory(
    Company,
    Office,
    extra=1,
    can_delete=False,
    fields=('state', 'zip', 'city', 'country', 'address')
)


class CompanyAdminForm(forms.ModelForm):
    """This form used as base for CompanyCreateForm
    We refused from use base image field 'cause we don't save one image.
    After user chose some image we run celery task which the crop this image
    also we create several different images (with different size)
    and store in the 'Images model

    images field - CharField, example:
    {
        'id': 0,
        'source': 'example.jpg',
        'width': 434.4,
        'height': 434.4,
        'rotate': 0,
        'x': 0,
        'y': 101.55283018867921,
        'scaleY': 1,
        'scaleX': 1
    }
    This information will be transmitted using js
    (/psc/static/js/widget/images_crop.js)

    all necessary information to crop and save images
    """
    images_to_delete = forms.CharField(
        widget=forms.HiddenInput, required=False)
    images = forms.CharField(
        widget=ImageCropWidget, required=False, label='Company Logo')

    def __init__(self, *args, **kwargs):
        super(CompanyAdminForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            images = CompanyImages.objects.filter(
                company=self.instance,
                path__contains='lg',
                crop_type=CompanyImages.CROP_TYPE_COMPANY
            )

            images_exists = CompanyImages.objects.filter(
                company=self.instance, is_edited_outside=True).exists()

            if images_exists:
                positions = CompanyImages.objects.filter(
                    company=self.instance).values_list(
                    'product_position', flat=True)

                # Check that all cover (lg_pr) exists
                if positions != images.count:
                    images_positions = images.values_list(
                        'product_position', flat=True)

                    # Convert queryset to list for append fake images
                    # with default cover
                    images = list(images)

                    # Finding what images are missing
                    difference = list(set(positions) - set(images_positions))

                    for position in difference:
                        company_image_id = CompanyImages.objects.filter(
                            product_position=position,
                            company=self.instance).first().id
                        # Create Fake Image Cover to show it
                        images.append({
                            'id': company_image_id,
                            'is_edited_outside': True,
                            'is_fake': True,
                            'product_position': position
                        })

            self.fields['images'].widget = ImageCropWidget(
                images_queryset=images, is_single=True, is_company=True)
            # self.fields['headquarter'].queryst = Office.objects.filter(
            #     company=self.instance)
        else:
            self.fields['images'].widget = ImageCropWidget(
                is_single=True, is_company=True)
            # self.fields['headquarter'].queryset = Office.objects.none()
        self.fields['country'].required = True

    class Meta:
        model = Company
        fields = "__all__"
        exclude = ('headquarter', )

    # def clean(self):
    #     instance = self.instance if self.instance.id else None
    #     office_formset_data = OfficeFormFactory(self.data, instance=instance)
    #     if not office_formset_data.is_valid():
    #         raise forms.ValidationError('One of office not valid')

    def clean_account(self):
        # Check that Company can be created and assigned to given account
        account = self.cleaned_data['account']
        company_count = account.company_set.filter(is_active=True).count()

        # Check that it's update and have assigned account
        if not hasattr(self.instance, 'account') or self.instance.account.id != account.id:
            company_count += 1  # counting that we wanna create

        # Check that Company count not graiter then max count
        # and account can have multiple companies
        max_company_count = settings.MAX_COMPANY_PER_ACCOUNT
        if account.is_multiple_company and company_count > max_company_count:

            error_message = 'Selected Account has reach max ' \
                            'count of companies ({})'.format(max_company_count)
            raise forms.ValidationError(error_message)

        # If account can have multiple companies
        # check that it's only one company for this account
        elif not account.is_multiple_company and company_count > 1:
            error_message = 'Selected Account can have only one Company'
            raise forms.ValidationError(error_message)

        return account

    def clean_images_to_delete(self):
        data = self.cleaned_data['images_to_delete']
        # Check that images set to delete have correct format
        if data:
            try:
                data = json.loads(data)
            except ValueError:
                raise forms.ValidationError('Wrong json format')
        return data

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
            images_count = self.instance.companyimages_set.all().count()

            if not images_count:
                raise forms.ValidationError(at_least_one_error)

            # Check that previous images was not set to delete
            elif self.cleaned_data['images_to_delete']:
                collected_ids = []
                images = CompanyImages.objects.filter(
                    id__in=self.cleaned_data['images_to_delete'])

                for image in images:
                    collected_ids += CompanyImages.objects.filter(
                        company=image.company,
                        product_position=image.product_position
                    ).values_list('id', flat=True)

                images_check = self.instance.companyimages_set.all().exclude(
                    id__in=collected_ids)

                if not images_check:
                    raise forms.ValidationError(at_least_one_error)

        elif not self.instance.pk:
            raise forms.ValidationError(at_least_one_error)

        return images_data

    def save(self, commit=True, user=None):
        """Override base save method.
        Main reason - we run celery task who crop our image and save
        several different images for current company with different size
        """
        company = super(CompanyAdminForm, self).save(commit)
        if user and not company.created_by:
            company.created_by = user
        else:
            company.edited_by = user
        company.save()

        if self.cleaned_data['images_to_delete']:
            # Send Celery task to delete images that was set to delete
            remove_images.delay(self.cleaned_data['images_to_delete'])

        # Send Celery task to crop all images
        crop_company_image.delay(self.cleaned_data['images'], company)

        return company


class CompanyCreateForm(CompanyAdminForm):
    account = forms.ModelChoiceField(
        queryset=Account.objects.all(), widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(CompanyCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Company
        exclude = ('created_by', 'edited_by', 'is_approved', 'headquarter',
                   'is_active')


class CompanyImageForm(ImageAdminForm):

    class Meta:
        model = CompanyImages
        exclude = fields = ("image", "crop_type", "company")
        widgets = {
            'company': autocomplete.ModelSelect2(url='companies:autocomplete')
        }
