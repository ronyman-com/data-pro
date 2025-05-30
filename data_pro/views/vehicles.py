from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from data_pro.models.vehicles import *
from data_pro.forms.vehicles import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


class VehicleStatusView(View):
    def get(self, request, pk, *args, **kwargs):
        try:
            vehicle = get_object_or_404(Vehicle, pk=pk)
            return JsonResponse({
                'id': vehicle.id,
                'status': vehicle.status,  # Adjust field name as needed
                'registration_number': vehicle.registration_number  # Example field
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def post(self, request, pk, *args, **kwargs):
        try:
            vehicle = get_object_or_404(Vehicle, pk=pk)
            new_status = request.POST.get('status')
            
            # Add status validation if needed
            # if new_status not in [choices...]:
            #     return JsonResponse({'error': 'Invalid status'}, status=400)
            
            vehicle.status = new_status
            vehicle.save()
            
            return JsonResponse({
                'message': 'Vehicle status updated successfully',
                'new_status': vehicle.status
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

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