import os

from django.core.files.base import ContentFile
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404
from django.views.generic.base import View
from django.http.response import JsonResponse
from django.conf import settings
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from dal import autocomplete

from psc.product.forms import (
    ProductCreateAdminForm, DocumentationFormFactory, VideoFormFactory)
from psc.product.models import Product


class ProductList(LoginRequiredMixin, ListView):
    template_name = 'product/list.html'

    def get_queryset(self):
        accout = self.request.user.get_account()
        return Product.objects.filter(
            Q(created_by__account=accout) |
            Q(created_by__owner=accout)
        )


class ProductCreateView(LoginRequiredMixin, FormView):
    template_name = 'product/create.html'
    form_class = ProductCreateAdminForm
    success_url = '/products/'

    def get_context_data(self, **kwargs):
        # Override method to pass Video and Documentation forms to context

        instance = getattr(self, 'instance', None)
        context = super(ProductCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['doc_form'] = DocumentationFormFactory(self.request.POST, self.request.FILES, instance=instance)
            context['video_form'] = VideoFormFactory(self.request.POST, instance=instance)
        else:
            context['doc_form'] = DocumentationFormFactory(instance=instance)
            context['video_form'] = VideoFormFactory(instance=instance)
        return context

    def get_form_kwargs(self):
        # Override method to path the user to form init
        kwargs = super(ProductCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Override method to set logic after form is_valid == True
        context = self.get_context_data()
        doc_form = context['doc_form']
        video_form = context['video_form']
        # Validate Documentation and Video forms
        if doc_form.is_valid() and video_form.is_valid():
            # Save everything after all validation passes
            self.object = form.save(user=self.request.user)
            doc_form.instance = self.object
            doc_form.save()
            video_form.instance = self.object
            video_form.save()
            return super(ProductCreateView, self).form_valid(form)
        else:
            # Render forms with error if any
            return self.render_to_response(self.get_context_data(form=form))


class UploadFile(View):

    def post(self, request):
        # Save source image for image crop widget
        max_upload_size = settings.PRODUCT_MAX_UPLOAD_SIZE

        if request.POST.get('is_company', None):
            max_upload_size = settings.COMPANY_MAX_UPLOAD_SIZE

        uploaded_filename = request.FILES['file'].name
        full_filename = os.path.join(settings.MEDIA_ROOT, uploaded_filename)
        fout = open(full_filename, 'wb+')
        file_content = ContentFile(request.FILES['file'].read())
        if file_content._size > max_upload_size:
            return JsonResponse({'error': "File too big."})
        for chunk in file_content.chunks():
            fout.write(chunk)
        fout.close()

        return JsonResponse({'url': '/media/{}'.format(uploaded_filename)})


class ProductEditView(ProductCreateView):

    def get_form_kwargs(self):
        form_kwargs = super(ProductEditView, self).get_form_kwargs()
        form_kwargs['instance'] = get_object_or_404(
            Product, id=self.kwargs.get('pk', None), is_active=True)
        self.instance = form_kwargs['instance']
        return form_kwargs

    def get_context_data(self, **kwargs):
        self.instance = get_object_or_404(Product, id=self.kwargs.get('pk', None))
        context = super(ProductEditView, self).get_context_data(**kwargs)
        context['error'] = ''
        return context


class ProductAutocomplete(autocomplete.Select2QuerySetView):
    """View which helps to work with django-autocomplete-light
    """
    def get_queryset(self):
        """Available Products to display in autocomplete field.
        Used only in the admin panel, so it is only available for
        administrator and staff
        """
        user = self.request.user
        if not user.is_authenticated() and not user.is_staff:
            return Product.objects.none()

        qs = Product.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs
