from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('SUPERADMIN', 'Super Admin'),
        ('CLIENT_ADMIN', 'Client Admin'), 
        ('USER', 'Regular User'),
    ]
    
    # Custom fields
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='USER'
    )
    client = models.ForeignKey(
        'clients.Client',  # Make sure 'clients' is your app name
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username