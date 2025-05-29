from django.views.generic import (
    ListView, CreateView, UpdateView, 
    DetailView, DeleteView, TemplateView
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from data_pro.models.passports import *
from data_pro.forms.passports import *

# ... (Keep all existing passport views) ...

class PassportExtensionListView(LoginRequiredMixin, ListView):
    model = PassportExtension
    template_name = 'admin/passports/extension_list.html'
    context_object_name = 'extensions'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        if not (self.request.user.is_superuser or self.request.user.user_type == 'SUPERADMIN'):
            queryset = queryset.filter(passport__customer__client=self.request.user.client)
        return queryset.select_related('passport', 'handed_by')

class PassportExtensionCreateView(LoginRequiredMixin, CreateView):
    model = PassportExtension
    form_class = PassportExtensionForm
    template_name = 'admin/passports/extension_create.html'
    success_url = reverse_lazy('data_pro:passport-extension-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.passport.status = 'in_process'
        form.instance.passport.save()
        messages.success(self.request, _('Passport extension application submitted successfully'))
        return super().form_valid(form)

class PassportExtensionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PassportExtension
    form_class = PassportExtensionForm
    template_name = 'admin/passports/extension_update.html'
    success_url = reverse_lazy('data_pro:passport-extension-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        extension = self.get_object()
        return extension.passport.customer.client == self.request.user.client

    def form_valid(self, form):
        messages.success(self.request, _('Passport extension updated successfully'))
        return super().form_valid(form)

class PassportExtensionDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = PassportExtension
    template_name = 'admin/passports/extension_detail.html'
    context_object_name = 'extension'

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        extension = self.get_object()
        return extension.passport.customer.client == self.request.user.client

class PassportExtensionCompleteView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PassportExtension
    fields = ['released_date', 'picked_by', 'handed_by', 'notes']
    template_name = 'admin/passports/extension_complete.html'

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        extension = self.get_object()
        return (extension.passport.customer.client == self.request.user.client and 
                self.request.user.user_type == 'CLIENT_ADMIN')

    def form_valid(self, form):
        extension = form.save(commit=False)
        extension.passport.status = 'valid'
        
        # Update passport expiry date based on extension duration
        if extension.released_date:
            from dateutil.relativedelta import relativedelta
            extension.passport.expiry_date = extension.released_date + relativedelta(months=extension.duration)
        
        extension.passport.save()
        extension.save()
        messages.success(self.request, _('Passport extension marked as completed'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('data_pro:passport-extension-detail', kwargs={'pk': self.object.pk})