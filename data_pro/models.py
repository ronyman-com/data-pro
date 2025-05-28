from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('SUPERADMIN', 'Super Admin'),
        ('CLIENT_ADMIN', 'Client Admin'),
        ('STAFF', 'Staff'),
        ('CUSTOMER', 'Customer'),
    )
    
    # Custom fields
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    client = models.ForeignKey('Client', on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=20)
    is_visible = models.BooleanField(default=True)

    
    def is_superadmin(self):
        return self.user_type == 'SUPERADMIN' or self.is_superuser
    
    def is_client_admin(self):
        return self.user_type == 'CLIENT_ADMIN'
    
    # Fix for group/permission conflicts
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name='custom_user_set',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='custom_user_set',
        related_query_name='user',
    )
    
    class Meta:
        db_table = 'custom_users'

class Client(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    

    



    
    