from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from data_pro.models.visas import *
from data_pro.forms.visas import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


class VisaStatusView(View):
    def get(self, request, pk, *args, **kwargs):
        try:
            visa = get_object_or_404(Visa, pk=pk)
            return JsonResponse({
                'id': visa.id,
                'status': visa.status,
                'visa_number': visa.visa_number  # Example field
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def post(self, request, pk, *args, **kwargs):
        try:
            visa = get_object_or_404(Visa, pk=pk)
            new_status = request.POST.get('status')
            
            # Add status validation if needed
            visa.status = new_status
            visa.save()
            
            return JsonResponse({
                'message': 'Visa status updated successfully',
                'new_status': visa.status
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
class VisaListView(LoginRequiredMixin, ListView):
    model = Visa
    template_name = 'admin/visas/list.html'
    context_object_name = 'visas'
    paginate_by = 10

class VisaCreateView(LoginRequiredMixin, CreateView):
    model = Visa
    form_class = VisaForm
    template_name = 'admin/visas/create.html'
    success_url = reverse_lazy('data_pro:visa-list')

class VisaDetailView(LoginRequiredMixin, DetailView):
    model = Visa
    template_name = 'admin/visas/detail.html'
    context_object_name = 'visa'

class VisaUpdateView(LoginRequiredMixin, UpdateView):
    model = Visa
    form_class = VisaForm
    template_name = 'admin/visas/update.html'
    success_url = reverse_lazy('data_pro:visa-list')

class VisaDeleteView(LoginRequiredMixin, DeleteView):
    model = Visa
    template_name = 'admin/visas/delete.html'
    success_url = reverse_lazy('data_pro:visa-list')