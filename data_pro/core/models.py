from django.db import models
from data_pro.models import User


class TrackedModel(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Office(TrackedModel):
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Airport(TrackedModel):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Vehicle(TrackedModel):
    VEHICLE_TYPES = (
        ('STANDARD', 'Standard ($100)'),
        ('VIP', 'VIP ($200)'),
    )
    
    registration_number = models.CharField(max_length=50, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    capacity = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.get_vehicle_type_display()} - {self.registration_number}"

class Customer(TrackedModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    date_of_birth = models.DateField()
    nationality = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Passport(TrackedModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    passport_number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    issuing_country = models.CharField(max_length=100)
    in_date = models.DateField()
    service_extension_duration = models.PositiveIntegerField(help_text="Duration in days")
    service_cost_usd = models.DecimalField(max_digits=10, decimal_places=2)
    release_date = models.DateField(null=True, blank=True)
    picked_up_by = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.passport_number} - {self.customer}"

class Visa(TrackedModel):
    VISA_TYPES = (
        ('TOURIST', 'Tourist Visa'),
        ('BUSINESS', 'Business Visa'),
        ('WORK', 'Work Permit'),
        ('STUDENT', 'Student Visa'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    passport = models.ForeignKey(Passport, on_delete=models.CASCADE)
    visa_type = models.CharField(max_length=20, choices=VISA_TYPES)
    visa_number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    paid_date = models.DateField(null=True, blank=True)
    released_date = models.DateField(null=True, blank=True)
    picked_up_by = models.CharField(max_length=255, null=True, blank=True)
    given_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.visa_number} - {self.customer}"

class TransportService(TrackedModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True)
    pickup_location = models.ForeignKey(Airport, on_delete=models.SET_NULL, null=True, related_name='pickups')
    dropoff_location = models.ForeignKey(Office, on_delete=models.SET_NULL, null=True, related_name='dropoffs')
    pickup_time = models.DateTimeField()
    dropoff_time = models.DateTimeField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_completed = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.price:
            self.price = 100 if self.vehicle.vehicle_type == 'STANDARD' else 200
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Transport for {self.customer}"

class Invoice(TrackedModel):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
    )
    
    invoice_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return self.invoice_number

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    @property
    def total(self):
        return self.quantity * self.unit_price * (1 + self.tax_rate / 100)
    
    def __str__(self):
        return f"{self.description} - {self.invoice}"