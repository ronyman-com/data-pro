# data_pro/api/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .permissions import IsClientAdminOrReadOnly
from .serializers import (
    CustomerSerializer,
    VisaSerializer,
    PassportSerializer,
    InvoiceSerializer,
    VehicleSerializer,
    TransportServiceSerializer
)
from data_pro.models.clients import *
from data_pro.models.invoices import *
from data_pro.models.transports import *
from data_pro.models.customers import *
from data_pro.models.vehicles import *
from data_pro.models.visas import *
from data_pro.models.passports import *
import csv
import io
from django.http import HttpResponse

class BaseViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet with common functionality for all models
    """
    permission_classes = [permissions.IsAuthenticated, IsClientAdminOrReadOnly]
    
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.user_type == 'CLIENT_ADMIN':
            qs = qs.filter(created_by__client=self.request.user.client)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def status(self, request, pk=None):
        obj = self.get_object()
        new_status = request.data.get('status')
        
        if hasattr(obj, 'update_status'):
            # Use model's update_status method if available
            success = obj.update_status(new_status, self.request.user)
        else:
            # Fallback to direct status update
            obj.status = new_status
            obj.save()
            success = True
            
        if success:
            return Response(self.get_serializer(obj).data)
        return Response(
            {'error': 'Invalid status transition'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

class CustomerViewSet(BaseViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    
    @action(detail=False, methods=['post'])
    def import_csv(self, request):
        """Handle CSV import of customers"""
        try:
            csv_file = request.FILES['file']
            data_set = csv_file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            next(io_string)  # Skip header
            
            for row in csv.reader(io_string):
                Customer.objects.update_or_create(
                    email=row[2],
                    defaults={
                        'name': row[1],
                        'phone': row[3],
                        'client': request.user.client
                    }
                )
            return Response(
                {'message': 'Customers imported successfully'},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Export customers as CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="customers.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Name', 'Email', 'Phone'])
        
        queryset = self.filter_queryset(self.get_queryset())
        for customer in queryset:
            writer.writerow([
                customer.id,
                customer.name,
                customer.email,
                customer.phone
            ])
            
        return response

class VisaViewSet(BaseViewSet):
    queryset = Visa.objects.all()
    serializer_class = VisaSerializer

class PassportViewSet(BaseViewSet):
    queryset = Passport.objects.all()
    serializer_class = PassportSerializer

class InvoiceViewSet(BaseViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        invoice = self.get_object()
        invoice.status = 'paid'
        invoice.payment_date = timezone.now()
        invoice.save()
        return Response({'status': 'paid'})

class VehicleViewSet(BaseViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    
    @action(detail=True, methods=['post'])
    def maintenance(self, request, pk=None):
        vehicle = self.get_object()
        vehicle.status = 'maintenance'
        vehicle.save()
        return Response({'status': 'maintenance'})

class TransportServiceViewSet(BaseViewSet):
    queryset = TransportService.objects.all()
    serializer_class = TransportServiceSerializer
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active transports (scheduled or in transit)"""
        queryset = self.get_queryset().filter(
            status__in=['scheduled', 'in_transit']
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Get completed transports"""
        queryset = self.get_queryset().filter(status='delivered')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def track(self, request, pk=None):
        """Update transport's current location"""
        transport = self.get_object()
        location = request.data.get('location')
        
        if not location:
            return Response(
                {'error': 'Location is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        transport.current_location = location
        transport.save()
        return Response({'location': location})