from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('SUPERADMIN', 'Super Admin'),
        ('CLIENT_ADMIN', 'Client Admin'), 
        ('USER', 'Regular User'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='USER')
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username