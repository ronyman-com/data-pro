from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from data_pro.models.transports import *
from data_pro.forms.transports import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from data_pro.models.transports import TransportService
from data_pro.api.serializers import TransportServiceSerializer
from data_pro.api.permissions import IsClientAdminOrReadOnly

class TransportServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing TransportService instances.
    Provides standard CRUD operations plus custom status actions.
    """
    queryset = TransportService.objects.all()
    serializer_class = TransportServiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsClientAdminOrReadOnly]

    def get_queryset(self):
        """
        Filter transports by client if user is CLIENT_ADMIN
        """
        qs = super().get_queryset()
        if self.request.user.user_type == 'CLIENT_ADMIN':
            qs = qs.filter(created_by__client=self.request.user.client)
        return qs

    def perform_create(self, serializer):
        """
        Set created_by and updated_by on creation
        """
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )

    def perform_update(self, serializer):
        """
        Update updated_by on modification
        """
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['get', 'post'])
    def status(self, request, pk=None):
        """
        Custom endpoint to get or update transport status
        """
        transport = self.get_object()
        
        if request.method == 'POST':
            new_status = request.data.get('status')
            
            # Validate status transition if needed
            # if not self.is_valid_status_transition(transport.status, new_status):
            #     return Response(
            #         {'error': 'Invalid status transition'},
            #         status=status.HTTP_400_BAD_REQUEST
            #     )
            
            transport.status = new_status
            
            # Automatically set timestamps based on status
            if new_status == 'in_transit':
                transport.departure_time = timezone.now()
            elif new_status == 'delivered':
                transport.arrival_time = timezone.now()
            
            transport.save()
            
            return Response({
                'status': transport.status,
                'departure_time': transport.departure_time,
                'arrival_time': transport.arrival_time,
                'message': 'Status updated successfully'
            })
        
        # GET request - return current status
        return Response({
            'status': transport.status,
            'departure_time': transport.departure_time,
            'arrival_time': transport.arrival_time,
            'current_location': transport.current_location
        })

    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Custom endpoint to get active transports
        """
        active_transports = self.get_queryset().filter(
            status__in=['scheduled', 'in_transit']
        )
        serializer = self.get_serializer(active_transports, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def completed(self, request):
        """
        Custom endpoint to get completed transports
        """
        completed_transports = self.get_queryset().filter(
            status='delivered'
        )
        serializer = self.get_serializer(completed_transports, many=True)
        return Response(serializer.data)

    # Helper method for status validation (example)
    def is_valid_status_transition(self, current_status, new_status):
        """
        Validate if the status transition is allowed
        """
        valid_transitions = {
            'scheduled': ['in_transit', 'cancelled'],
            'in_transit': ['delivered', 'cancelled'],
            # Add other valid transitions
        }
        return new_status in valid_transitions.get(current_status, [])

class TransportStatusView(View):
    def get(self, request, pk, *args, **kwargs):
        """
        Retrieve the current status of a transport
        """
        try:
            transport = get_object_or_404(Transport, pk=pk)
            return JsonResponse({
                'id': transport.id,
                'status': transport.status,
                'transport_reference': transport.reference_number,  # Example field
                'current_location': transport.current_location,    # Example field
                'departure_time': transport.departure_time.isoformat() if transport.departure_time else None,
                'arrival_time': transport.arrival_time.isoformat() if transport.arrival_time else None
                # Add other relevant fields from your Transport model
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def post(self, request, pk, *args, **kwargs):
        """
        Update the status of a transport
        """
        try:
            transport = get_object_or_404(Transport, pk=pk)
            new_status = request.POST.get('status')
            
            # Add any status validation if your model has specific status choices
            # Example:
            # valid_statuses = [choice[0] for choice in Transport.STATUS_CHOICES]
            # if new_status not in valid_statuses:
            #     return JsonResponse({'error': 'Invalid status value'}, status=400)
            
            transport.status = new_status
            
            # You might want to add additional status-related updates
            if new_status == 'in_transit':
                transport.departure_time = timezone.now()
            elif new_status == 'delivered':
                transport.arrival_time = timezone.now()
            
            transport.save()
            
            return JsonResponse({
                'message': 'Transport status updated successfully',
                'new_status': transport.status,
                'updated_fields': {
                    'status': transport.status,
                    'departure_time': transport.departure_time.isoformat() if transport.departure_time else None,
                    'arrival_time': transport.arrival_time.isoformat() if transport.arrival_time else None
                }
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

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