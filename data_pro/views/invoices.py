from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from data_pro.models.invoices import *
from data_pro.forms.invoices import *
from django.contrib.auth.mixins import LoginRequiredMixin

class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'admin/invoices/list.html'
    context_object_name = 'invoices'
    paginate_by = 10

class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'admin/invoices/create.html'
    success_url = reverse_lazy('data_pro:invoice-list')

class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'admin/invoices/detail.html'
    context_object_name = 'invoice'

class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'admin/invoices/update.html'
    success_url = reverse_lazy('data_pro:invoice-list')

class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Invoice
    template_name = 'admin/invoices/delete.html'
    success_url = reverse_lazy('data_pro:invoice-list')