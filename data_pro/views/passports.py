from django.views.generic import (
    ListView, CreateView, UpdateView, 
    DetailView, DeleteView, TemplateView
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone

from data_pro.models.passports import *
from data_pro.forms.passports import *
from data_pro.models.customers import *


class PassportListView(ListView):
    model = Passport
    paginate_by = 20
    template_name = 'admin/passports/list.html'
    context_object_name = 'passports'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('customer')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(passport_number__icontains=search_query) |
                Q(customer__first_name__icontains=search_query) |
                Q(customer__last_name__icontains=search_query) |
                Q(issuing_country__icontains=search_query))
        
        # Status filter
        status_filter = self.request.GET.get('status')
        if status_filter:
            if status_filter == 'valid':
                queryset = queryset.filter(expiry_date__gte=timezone.now().date())
            elif status_filter == 'expired':
                queryset = queryset.filter(expiry_date__lt=timezone.now().date())
            elif status_filter == 'in_process':
                queryset = queryset.filter(status='in_process')
            elif status_filter == 'released':
                queryset = queryset.filter(status='released')
        
        return queryset.order_by('-issue_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_passports'] = self.get_queryset().count()
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            passports = context['object_list']
            data = [{
                'id': passport.id,
                'passport_number': passport.passport_number,
                'customer': str(passport.customer),
                'issue_date': passport.issue_date.strftime('%Y-%m-%d') if passport.issue_date else None,
                'expiry_date': passport.expiry_date.strftime('%Y-%m-%d') if passport.expiry_date else None,
                'issuing_country': passport.issuing_country,
                'service_cost_usd': str(passport.service_cost_usd),
                'status': passport.status,
                'actions': f'<a href="{reverse_lazy("data_pro:passport-update", kwargs={"pk": passport.id})}" class="btn btn-sm btn-warning"><i class="bi bi-pencil"></i></a> '
                          f'<a href="{reverse_lazy("data_pro:passport-detail", kwargs={"pk": passport.id})}" class="btn btn-sm btn-info"><i class="bi bi-eye"></i></a>'
            } for passport in passports]
            
            return JsonResponse({
                'passports': data,
                'count': context['paginator'].count,
                'page': context['page_obj'].number,
                'total_pages': context['paginator'].num_pages
            })
        return super().render_to_response(context, **response_kwargs)


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


class PassportCreateView(LoginRequiredMixin, CreateView):
    model = Passport
    form_class = PassportForm
    template_name = 'admin/passports/create.html'

    def get_success_url(self):
        messages.success(self.request, "Passport created successfully")
        return reverse_lazy('system:customer-detail', kwargs={'pk': self.kwargs['customer_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customer'] = Customer.objects.get(pk=self.kwargs['customer_id'])
        return context

    def form_valid(self, form):
        form.instance.customer_id = self.kwargs['customer_id']
        return super().form_valid(form)


class PassportUpdateView(LoginRequiredMixin, UpdateView):
    model = Passport
    form_class = PassportForm
    template_name = 'admin/passports/update.html'

    def get_success_url(self):
        messages.success(self.request, "Passport updated successfully")
        return reverse_lazy('system:customer-detail', kwargs={'pk': self.object.customer.pk})


class PassportDeleteView(LoginRequiredMixin, DeleteView):
    model = Passport
    template_name = 'admin/passports/delete.html'

    def get_success_url(self):
        messages.success(self.request, "Passport deleted successfully")
        return reverse_lazy('system:customer-detail', kwargs={'pk': self.object.customer.pk})


class PassportStatusView(LoginRequiredMixin, UpdateView):
    model = Passport
    fields = ['status']
    template_name = 'admin/passports/status.html'

    def get_success_url(self):
        messages.success(self.request, "Passport status updated")
        return reverse_lazy('system:customer-detail', kwargs={'pk': self.object.customer.pk})