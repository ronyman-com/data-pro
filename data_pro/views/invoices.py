from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from data_pro.models.invoices import *
from data_pro.forms.invoices import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


class InvoiceStatusView(View):
    def get(self, request, pk, *args, **kwargs):
        try:
            invoice = get_object_or_404(Invoice, pk=pk)
            return JsonResponse({
                'id': invoice.id,
                'status': invoice.status,
                'invoice_number': invoice.invoice_number,  # Example field
                'amount': str(invoice.amount)  # Example field
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def post(self, request, pk, *args, **kwargs):
        try:
            invoice = get_object_or_404(Invoice, pk=pk)
            new_status = request.POST.get('status')
            
            # Add status validation if needed
            invoice.status = new_status
            invoice.save()
            
            return JsonResponse({
                'message': 'Invoice status updated successfully',
                'new_status': invoice.status
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

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