from rest_framework import serializers
from data_pro.core.models import Customer, Visa, Passport, Invoice, Vehicle, TransportService

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by', 'created_at', 'updated_at')

class VisaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visa
        fields = '__all__'

class PassportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passport
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

class TransportServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportService
        fields = '__all__'