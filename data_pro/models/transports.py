from django.db import models
from django.db import models
from django.contrib.auth import get_user_model
from .customers import *
from .vehicles import *
from .clients import *

User = get_user_model()

class TransportService(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('on_hold', 'On Hold'),
    )

    # Core transport information
    reference_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='transport_services')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_transports')
    
    # Location details
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    current_location = models.CharField(max_length=255, blank=True, null=True)
    
    # Timing information
    scheduled_departure = models.DateTimeField()
    scheduled_arrival = models.DateTimeField()
    actual_departure = models.DateTimeField(null=True, blank=True)
    actual_arrival = models.DateTimeField(null=True, blank=True)
    
    # Transport metrics
    distance_km = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_duration_hours = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    tracking_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    
    # Financial information
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    additional_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Additional details
    special_instructions = models.TextField(blank=True, null=True)
    required_documents = models.TextField(blank=True, null=True)
    
    # Audit fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_transports')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_transports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Client relationship
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='transports')

    def __str__(self):
        return f"{self.reference_number} - {self.get_status_display()} ({self.origin} → {self.destination})"

    @property
    def total_fare(self):
        return self.base_fare + self.additional_charges - self.discount

    @property
    def is_active(self):
        return self.status in ['scheduled', 'in_transit']

    @property
    def is_completed(self):
        return self.status == 'delivered'

    def update_status(self, new_status, user=None):
        """Helper method to safely update transport status"""
        valid_transitions = {
            'scheduled': ['in_transit', 'cancelled', 'on_hold'],
            'in_transit': ['delivered', 'cancelled', 'on_hold'],
            'on_hold': ['in_transit', 'cancelled'],
        }
        
        if new_status in valid_transitions.get(self.status, []):
            self.status = new_status
            if new_status == 'in_transit':
                self.actual_departure = timezone.now()
            elif new_status == 'delivered':
                self.actual_arrival = timezone.now()
            
            if user:
                self.updated_by = user
            self.save()
            return True
        return False

    class Meta:
        ordering = ['-scheduled_departure']
        verbose_name = 'Transport Service'
        verbose_name_plural = 'Transport Services'
        indexes = [
            models.Index(fields=['reference_number']),
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_departure']),
        ]

class Transport(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='transports')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='transports')
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    pickup_time = models.DateTimeField()
    dropoff_time = models.DateTimeField()
    distance = models.DecimalField(max_digits=10, decimal_places=2)
    fare = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transport #{self.id} - {self.customer}"

    class Meta:
        ordering = ['-pickup_time']