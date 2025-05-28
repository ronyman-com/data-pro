# data_pro/admin/client.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from data_pro.models import Client
from .mixins import SuperAdminMixin

class ClientListView(SuperAdminMixin, ListView):
    model = Client
    template_name = 'admin/clients/list.html'
    context_object_name = 'clients'
    
    def get_queryset(self):
        return Client.objects.all().order_by('-created_at')

class ClientCreateView(SuperAdminMixin, CreateView):
    model = Client
    fields = ['name', 'is_active']
    template_name = 'admin/clients/form.html'
    success_url = reverse_lazy('data_pro:client-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Client "{self.object.name}" created successfully')
        return response

class ClientUpdateView(SuperAdminMixin, UpdateView):
    model = Client
    fields = ['name', 'is_active']
    template_name = 'admin/clients/form.html'
    
    def get_success_url(self):
        messages.success(self.request, f'Client "{self.object.name}" updated successfully')
        return reverse_lazy('data_pro:client-list')

class ClientDeleteView(SuperAdminMixin, DeleteView):
    model = Client
    template_name = 'admin/clients/confirm_delete.html'
    success_url = reverse_lazy('data_pro:client-list')
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Client deleted successfully')
        return response