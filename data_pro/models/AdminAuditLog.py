# Example AdminAuditLog model
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class AdminAuditLog(models.Model):
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='admin_actions')
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='user_audit_logs')
    action = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.admin} - {self.action} - {self.timestamp}"