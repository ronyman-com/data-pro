from rest_framework import viewsets, permissions
from data_pro.core.models import Customer, Visa, Passport, Invoice, Vehicle, TransportService
from .serializers import (
    CustomerSerializer, 
    VisaSerializer,
    PassportSerializer,
    InvoiceSerializer,
    VehicleSerializer,
    TransportServiceSerializer
)
from .permissions import IsClientAdminOrReadOnly

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsClientAdminOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.user_type == 'CLIENT_ADMIN':
            qs = qs.filter(created_by__client=self.request.user.client)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

# Similar viewset implementations for other models
class VisaViewSet(viewsets.ModelViewSet):
    queryset = Visa.objects.all()
    serializer_class = VisaSerializer
    permission_classes = [permissions.IsAuthenticated, IsClientAdminOrReadOnly]

class PassportViewSet(viewsets.ModelViewSet):
    queryset = Passport.objects.all()
    serializer_class = PassportSerializer
    permission_classes = [permissions.IsAuthenticated, IsClientAdminOrReadOnly]

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsClientAdminOrReadOnly]

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated, IsClientAdminOrReadOnly]

class TransportServiceViewSet(viewsets.ModelViewSet):
    queryset = TransportService.objects.all()
    serializer_class = TransportServiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsClientAdminOrReadOnly]