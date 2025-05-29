from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from data_pro.models.clients import *
from data_pro.forms.clients import *
from django.contrib.auth.mixins import LoginRequiredMixin

class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'admin/clients/list.html'
    context_object_name = 'clients'
    paginate_by = 10

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'admin/clients/create.html'
    success_url = reverse_lazy('data_pro:client-list')

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'admin/clients/update.html'
    success_url = reverse_lazy('data_pro:client-list')

class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'admin/clients/delete.html'
    success_url = reverse_lazy('data_pro:client-list')