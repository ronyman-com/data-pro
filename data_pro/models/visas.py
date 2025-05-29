from django.db import models
from .customers import Customer

class Visa(models.Model):
    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('issued', 'Issued'),
    )
    
    TYPE_CHOICES = (
        ('tourist', 'Tourist'),
        ('business', 'Business'),
        ('student', 'Student'),
        ('work', 'Work'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='visas')
    visa_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    country = models.CharField(max_length=100)
    application_date = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer} - {self.visa_type} Visa ({self.country})"

    class Meta:
        ordering = ['-application_date']