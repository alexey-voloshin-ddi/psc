psc
===

psc project

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django


Settings
--------

Moved to settings_.

.. _settings: http://cookiecutter-django.readthedocs.io/en/latest/settings.html

Basic Commands
--------------



Setting Up Your Users
^^^^^^^^^^^^^^^^^^^^^

* To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

* To create an **superuser account**, use this command::

    $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

Test coverage
^^^^^^^^^^^^^

To run the tests, check your test coverage, and generate an HTML coverage report::

    $ coverage run manage.py test
    $ coverage html
    $ open htmlcov/index.html

Running tests with py.test
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ py.test

Live reloading and Sass CSS compilation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Moved to `Live reloading and SASS compilation`_.

.. _`Live reloading and SASS compilation`: http://cookiecutter-django.readthedocs.io/en/latest/live-reloading-and-sass-compilation.html



Celery
^^^^^^

This app comes with Celery.

To run a celery worker:

.. code-block:: bash

    cd psc
    celery -A psc.taskapp worker -l info

Please note: For Celery's import magic to work, it is important *where* the celery commands are run. If you are in the same folder with *manage.py*, you should be right.





Deployment
----------

Application have two database so when you want run migrations please do not forget did migration for second database:

.. code-block:: bash

    python3 manage.py migrate --noinput
    python3 manage.py migrate --noinput --database='duplicate'


The following details how to deploy this application.





How it's works
--------------
Edited: (25 Aug. 2017)


Image Crop
^^^^^^^^^^


1. psc/templates/widgets/crop_widget.html it's a basic crop widget used in admin panel and web site for crop images
It is responsible for displaying pictures, adding, deleting and cropping

2. psc/static/js/widget/images_crop.js it's a core js used for upload image to server, selection pictures coordinates
for cropping and submit Ajax form

When user click by 'Upload image' button and choose a picture it is uploaded to the server (original)
psc/static/js/widget/images_crop.js `submitFormAjax` function line: 63

.. code-block:: javascript

    function submitFormAjax(file)
    {
        var csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;

        xmlhttp.open("POST","/products/upload/image/", true);
        ...
    }


After clicking on the save button we save the coordinates of the image cropping and other additional information
but do not send it to the server
psc/static/js/widget/images_crop.js line: 259

.. code-block:: javascript

    document.getElementById('save').onclick = function (e) {
        var clone = document.getElementById('to-clone').cloneNode(true);
        var data = cropper.getData();
        ...
    }

3. In order to send all manipulations with pictures to the server, we use the django form
After click button 'Create ...' (product, company or something else, where used cropping images)
We are submitting form to server.

Then the work of our forms: ProductCreateAdminForm or CompanyAdminForm

psc/product/forms.py `ProductCreateAdminForm` class line: 210

.. code-block:: python

    class ProductCreateAdminForm(forms.ModelForm):
        images_to_delete = forms.CharField(widget=forms.HiddenInput, required=False)
        images = forms.CharField(widget=ImageCropWidget, required=False)
        ...

psc/companies/forms.py `CompanyAdminForm` class line: 23

.. code-block:: python

    class CompanyAdminForm(forms.ModelForm):
        images_to_delete = forms.CharField(widget=forms.HiddenInput, required=False)
        images = forms.CharField(widget=ImageCropWidget, required=False, label='Company Logo')
        ...

In save methods you can see run crop tasks, example:
psc/companies/forms.py line: 215

.. code-block:: python

    # Send Celery task to crop all images
    crop_company_image.delay(self.cleaned_data['images'], company)

4. Celery task. This functions cropping images to setup sizes and selected crop coordinates.
Also here creating Image object and store in media cropped images.
psc/taskapp/tasks.py `crop_company_image` line: 70

.. code-block:: python

    @app.task
    def crop_company_image(images, company):
        for image_data in images:
            for key, size_data in settings.COMPANY_LOGO_SIZE.items():
                image_data['type'] = 'co'
                image_type = image_data['source'].split('.')[-1]
                image = CompanyImages.objects.create(
                    ...

and `crop_all_images` line: 96

.. code-block:: python

    @app.task
    def crop_all_images(images, product):
        for image_data in images:
            for type_key, sizes in settings.IMAGE_SIZES.items():
                image_data['type'] = type_key
                for key, size_data in sizes.items():
                    image_type = image_data['source'].split('.')[-1]
                    image = ImageModel.objects.create(
                    ...

Notification
^^^^^^^^^^^^

Platform support some notification, bellow list all notifications:

* user is approved (psc/users/models.py line: 78)

.. code-block:: python

    # create notification when user confirmed
    Notification.objects.create(
        user=self,
        type=Notification.TYPE_USER_CONFIRMED,
        instance_name=self.name
    )


* user is unapproved (psc/users/models.py line: 85)

.. code-block:: python

    # create notification when user approved or deny
    Notification.objects.create(
        user=self,
        type=notification_type,
        instance_name=self.name
    )

* user is delete (psc/users/models.py line: 132)

.. code-block:: python

    # create notification when user is removed
    Notification.objects.create(
        user=instance.account.owner,
        type=Notification.TYPE_USER_REMOVED,
        instance_name=instance.name
    )

* company is approved (psc/companies/models.py line: 39)
* company us unapproved (psc/companies/models.py line: 39)

.. code-block:: python

    # create notification when company approve or deny
    notification_type = Notification.TYPE_COMPANY_APPROVED if self.is_approved else Notification.TYPE_COMPANY_DENY
    Notification.objects.create(
        user=user,
        type=notification_type,
        instance_name=self.name
    )

* company is delete (psc/companies/models.py line: 94)

.. code-block:: python

    # create notification when product is removed
    Notification.objects.create(
        user=instance.account.owner,
        type=Notification.TYPE_COMPANY_REMOVED,
        instance_name=instance.name
    )

* product is approved (psc/product/models.py line: 43)
* product is unapproved (psc/product/models.py line: 43)

.. code-block:: python

    # create notification  when product is approved or deny
    notification_type = Notification.TYPE_PRODUCT_APPROVED if self.is_approved else Notification.TYPE_PRODUCT_DENY
    Notification.objects.create(
        user=user,
        type=notification_type,
        instance_name=self.name
    )

* product is delete (psc/product/models.py line: 156)

.. code-block:: python

    # create notification when product is removed
    Notification.objects.create(
        user=instance.company.account.owner,
        type=Notification.TYPE_PRODUCT_REMOVED,
        instance_name=instance.name
    )

* feature 'is multiple users' for account is activate (psc/accounts/models.py line: 28)
* feature 'is multiple company' for account is activate (psc/accounts/models.py line: 36)

.. code-block:: python

    # Create notification when `is_multiple_users is active
    Notification.objects.create(
        user=self.owner,
        type=Notification.TYPE_MULTIPLE_USER_ACTIVE,
        instance_name=self.__str__()
    )

    # Create notification when `is_multiple_company is active
    Notification.objects.create(
        user=self.owner,
        type=Notification.TYPE_MULTIPLE_COMPANY_ACTIVE,
        instance_name=self.__str__()
    )

All this notification will be created when did manipulation with object, so to work her no need some special steps.
Does not matter where was create edit or delete some objects (web interface, api or admin panel) notification will be created.


Invitation
^^^^^^^^^^

When you create invite some user to your platform we create invite object, you can saw it in
/admin/users/invitationkey/

If you need resend invite for user again you can use function on site /users/ (Resend button used api)
or use admin panel for this (invitationkey detail page - Resend invitation button).

Clicks to this buttons recreate invitation object and will be resend invite email to specified email address.

Resend button (web site) psc/api/views.py `InvitationViewSet` class line: 113

.. code-block:: python

    class InvitationViewSet(mixins.DestroyModelMixin, GenericViewSet):
        serializer_class = InvitationSerializer
        queryset = InvitationKey.objects.all()

Resend invitation button (admin panel) psc/users/views.py `ResendInvitation` class line: 143

.. code-block:: python

    class ResendInvitation(View):
        def get(self, request, pk):
            instance = get_object_or_404(InvitationKey, pk=pk)


Document and Video inlineformset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Product object form contains inline form to Document and Video objects
In django admin panel it's implement used django inline form

psc/product/admin.py line: 44

.. code-block:: python

    class ProductAdmin(admin.ModelAdmin):
        form = ProductCreateAdminForm
        inlines = (DocumentInline, VideoInline)

In web site used ProductCreateAdminForm psc/product/forms.py line: 210

.. code-block:: python

    class ProductCreateAdminForm(forms.ModelForm):
        images_to_delete = forms.CharField(widget=forms.HiddenInput, required=False)
        images = forms.CharField(widget=ImageCropWidget, required=False)

here we use VideoFormFactory and DocumentationFormFactory line: 261

.. code-block:: python

    def clean(self):
        # Validate inline models before save to not allow save product before documents and videos
        instance = self.instance if self.instance.id else None

        videos_formset_data = VideoFormFactory(self.data, instance=instance)
        documents_formset_data = DocumentationFormFactory(self.data, self.files, instance=instance)

This is sufficient to correctly store the resulting form.

But in web site we also need build correct form. For this we use psc/static/js/product.js

With this js file we build the correct form to send it to the server when you need to add more than one document or video.

Submission of the form occurs in the standard django solution.
