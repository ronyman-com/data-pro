from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from data_pro.models.transports import *
from data_pro.forms.transports import *
from django.contrib.auth.mixins import LoginRequiredMixin

class TransportListView(LoginRequiredMixin, ListView):
    model = Transport
    template_name = 'admin/transports/list.html'
    context_object_name = 'transports'
    paginate_by = 10

class TransportCreateView(LoginRequiredMixin, CreateView):
    model = Transport
    form_class = TransportForm
    template_name = 'admin/transports/create.html'
    success_url = reverse_lazy('data_pro:transport-list')

class TransportDetailView(LoginRequiredMixin, DetailView):
    model = Transport
    template_name = 'admin/transports/detail.html'
    context_object_name = 'transport'

class TransportUpdateView(LoginRequiredMixin, UpdateView):
    model = Transport
    form_class = TransportForm
    template_name = 'admin/transports/update.html'
    success_url = reverse_lazy('data_pro:transport-list')

class TransportDeleteView(LoginRequiredMixin, DeleteView):
    model = Transport
    template_name = 'admin/transports/delete.html'
    success_url = reverse_lazy('data_pro:transport-list')