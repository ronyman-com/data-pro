from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from data_pro.models.customers import *
from data_pro.forms.customers import *
from django.contrib.auth.mixins import LoginRequiredMixin

class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'admin/customers/list.html'
    context_object_name = 'customers'
    paginate_by = 10

class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'admin/customers/create.html'
    success_url = reverse_lazy('data_pro:customer-list')

class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'admin/customers/update.html'
    success_url = reverse_lazy('data_pro:customer-list')

class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    template_name = 'admin/customers/delete.html'
    success_url = reverse_lazy('data_pro:customer-list')