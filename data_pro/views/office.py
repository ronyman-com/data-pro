# data_pro/views/office.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from data_pro.models.office import *
from data_pro.forms.office import *
from django.contrib.auth.mixins import LoginRequiredMixin

class OfficeListView(LoginRequiredMixin, ListView):
    model = Office
    template_name = 'admin/office/list.html'
    context_object_name = 'offices'

class OfficeCreateView(LoginRequiredMixin, CreateView):
    model = Office
    form_class = OfficeForm
    template_name = 'admin/office/create.html'
    success_url = reverse_lazy('data_pro:office-list')

class OfficeUpdateView(LoginRequiredMixin, UpdateView):
    model = Office
    form_class = OfficeForm
    template_name = 'admin/office/update.html'
    success_url = reverse_lazy('data_pro:office-list')

class OfficeDeleteView(LoginRequiredMixin, DeleteView):
    model = Office
    template_name = 'admin/office/delete.html'
    success_url = reverse_lazy('data_pro:office-list')