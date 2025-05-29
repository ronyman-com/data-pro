from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from ..models import Vehicle
from ..forms import VehicleForm
from django.contrib.auth.mixins import LoginRequiredMixin

class VehicleListView(LoginRequiredMixin, ListView):
    model = Vehicle
    template_name = 'admin/vehicles/list.html'
    context_object_name = 'vehicles'
    paginate_by = 10

class VehicleCreateView(LoginRequiredMixin, CreateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'admin/vehicles/create.html'
    success_url = reverse_lazy('data_pro:vehicle-list')

class VehicleDetailView(LoginRequiredMixin, DetailView):
    model = Vehicle
    template_name = 'admin/vehicles/detail.html'
    context_object_name = 'vehicle'

class VehicleUpdateView(LoginRequiredMixin, UpdateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'admin/vehicles/update.html'
    success_url = reverse_lazy('data_pro:vehicle-list')

class VehicleDeleteView(LoginRequiredMixin, DeleteView):
    model = Vehicle
    template_name = 'admin/vehicles/delete.html'
    success_url = reverse_lazy('data_pro:vehicle-list')