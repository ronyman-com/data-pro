from django.views.generic import (
    ListView, CreateView, UpdateView, 
    DetailView, DeleteView
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.utils import timezone

from data_pro.models.visas import Visa
from data_pro.forms.visas import VisaForm
import pandas as pd
from io import BytesIO
from django.shortcuts import redirect

class VisaListView(LoginRequiredMixin, ListView):
    model = Visa
    template_name = 'admin/visas/list.html'
    paginate_by = 20
    context_object_name = 'visas'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('customer')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(visa_number__icontains=search_query) |
                Q(customer__first_name__icontains=search_query) |
                Q(customer__last_name__icontains=search_query)
            )
        
        # Status filter
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Date range filter
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date and end_date:
            try:
                start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(issue_date__range=[start_date, end_date])
            except ValueError:
                pass
        
        return queryset.order_by('-issue_date')

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            visas = context['object_list']
            data = [{
                'id': visa.id,
                'visa_number': visa.visa_number,
                'customer': str(visa.customer),
                'visa_type': visa.get_visa_type_display(),
                'issue_date': visa.issue_date.strftime('%Y-%m-%d') if visa.issue_date else None,
                'expiry_date': visa.expiry_date.strftime('%Y-%m-%d') if visa.expiry_date else None,
                'unit_cost': str(visa.unit_cost),
                'status': visa.get_status_display(),
                'actions': f'<a href="{reverse_lazy("data_pro:visa-update", kwargs={"pk": visa.id})}" class="btn btn-sm btn-warning"><i class="bi bi-pencil"></i></a> '
                          f'<a href="{reverse_lazy("data_pro:visa-detail", kwargs={"pk": visa.id})}" class="btn btn-sm btn-info"><i class="bi bi-eye"></i></a>'
            } for visa in visas]
            
            return JsonResponse({
                'visas': data,
                'count': context['paginator'].count,
                'page': context['page_obj'].number,
                'total_pages': context['paginator'].num_pages
            })
        return super().render_to_response(context, **response_kwargs)

class VisaCreateView(LoginRequiredMixin, CreateView):
    model = Visa
    form_class = VisaForm
    template_name = 'admin/visas/create.html'
    success_url = reverse_lazy('data_pro:visa-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Visa created successfully!'))
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Visa created successfully!',
                'redirect_url': self.success_url
            })
        return response

class VisaUpdateView(LoginRequiredMixin, UpdateView):
    model = Visa
    form_class = VisaForm
    template_name = 'admin/visas/update.html'
    success_url = reverse_lazy('data_pro:visa-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Visa updated successfully!'))
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Visa updated successfully!',
                'redirect_url': self.success_url
            })
        return response

class VisaDetailView(LoginRequiredMixin, DetailView):
    model = Visa
    template_name = 'admin/visas/detail.html'
    context_object_name = 'visa'

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            visa = context['visa']
            data = {
                'id': visa.id,
                'visa_number': visa.visa_number,
                'customer': str(visa.customer),
                'visa_type': visa.get_visa_type_display(),
                'issue_date': visa.issue_date.strftime('%Y-%m-%d') if visa.issue_date else None,
                'expiry_date': visa.expiry_date.strftime('%Y-%m-%d') if visa.expiry_date else None,
                'unit_cost': str(visa.unit_cost),
                'status': visa.get_status_display(),
                'notes': visa.notes,
                'created_at': visa.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': visa.updated_at.strftime('%Y-%m-%d %H:%M')
            }
            return JsonResponse(data)
        return super().render_to_response(context, **response_kwargs)

class VisaDeleteView(LoginRequiredMixin, DeleteView):
    model = Visa
    template_name = 'admin/visas/delete.html'
    success_url = reverse_lazy('data_pro:visa-list')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, _('Visa deleted successfully!'))
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Visa deleted successfully!',
                'redirect_url': self.success_url
            })
        return response

def visa_export(request):
    queryset = Visa.objects.all().select_related('customer')
    df = pd.DataFrame(list(queryset.values(
        'visa_number',
        'customer__first_name',
        'customer__last_name',
        'visa_type',
        'issue_date',
        'expiry_date',
        'unit_cost',
        'status',
        'notes'
    )))
    
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Visas', index=False)
    writer.close()
    output.seek(0)
    
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=visas_export.xlsx'
    return response

def visa_template(request):
    # Create template DataFrame with required columns
    df = pd.DataFrame(columns=[
        'visa_number',
        'customer_id',
        'visa_type',
        'issue_date',
        'expiry_date',
        'unit_cost',
        'status',
        'notes'
    ])
    
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Template', index=False)
    writer.close()
    output.seek(0)
    
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=visa_import_template.xlsx'
    return response



def visa_import(request):
    if request.method == 'POST':
        try:
            excel_file = request.FILES['excel_file']
            df = pd.read_excel(excel_file)
            
            # Process and validate the imported data
            for index, row in df.iterrows():
                Visa.objects.create(
                    visa_number=row['visa_number'],
                    customer_id=row['customer_id'],
                    visa_type=row['visa_type'],
                    issuing_country=row['issuing_country'],
                    issue_date=row['issue_date'],
                    expiry_date=row['expiry_date'],
                    status=row.get('status', 'processing'),
                    unit_cost=row['unit_cost'],
                    service_fee=row.get('service_fee', 0),
                )
            
            messages.success(request, 'Visas imported successfully!')
            return redirect('data_pro:visa-list')
            
        except Exception as e:
            messages.error(request, f'Error importing visas: {str(e)}')
            return redirect('data_pro:visa-list')
    
    return redirect('data_pro:visa-list')