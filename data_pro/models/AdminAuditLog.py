from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class AdminAuditLog(models.Model):
    ACTION_CHOICES = (
        ('create', _('Create')),
        ('update', _('Update')),
        ('delete', _('Delete')),
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('password_change', _('Password Change')),
    )

    admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='admin_actions',
        verbose_name=_('Administrator')
    )
    target_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_audit_logs',
        verbose_name=_('Target User')
    )
    action = models.CharField(
        _('Action'),
        max_length=50,
        choices=ACTION_CHOICES
    )
    timestamp = models.DateTimeField(
        _('Timestamp'),
        auto_now_add=True
    )
    ip_address = models.GenericIPAddressField(
        _('IP Address'),
        null=True,
        blank=True
    )
    additional_info = models.JSONField(
        _('Additional Information'),
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.admin or 'System'} - {self.get_action_display()} - {self.timestamp}"

    class Meta:
        verbose_name = _('Admin Audit Log')
        verbose_name_plural = _('Admin Audit Logs')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['action']),
            models.Index(fields=['admin']),
            models.Index(fields=['target_user']),
        ]
        permissions = [
            ('view_audit_log', _('Can view audit logs')),
            ('export_audit_log', _('Can export audit logs')),
        ]
        get_latest_by = 'timestamp'