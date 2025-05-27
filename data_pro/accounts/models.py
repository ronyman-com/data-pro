# datapro/data_pro/accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):  # Changed from 'user' to 'User'
    USER_TYPE_CHOICES = (
        ('SUPERADMIN', 'Super Admin'),
        ('CLIENT_ADMIN', 'Client Admin'),
        ('CUSTOMER', 'Customer'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    client = models.ForeignKey('Client', on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=20)
    is_visible = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if self.user_type == 'SUPERADMIN':
            self.is_visible = False
        super().save(*args, **kwargs)

class Client(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name