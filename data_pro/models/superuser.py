from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

User = get_user_model()

class AdminAuditLog(models.Model):
    """Tracks all administrative actions performed by superusers"""
    class ActionTypes(models.TextChoices):
        USER_CREATE = 'USER_CREATE', _('User Creation')
        USER_EDIT = 'USER_EDIT', _('User Modification')
        USER_DELETE = 'USER_DELETE', _('User Deletion')
        CLIENT_CREATE = 'CLIENT_CREATE', _('Client Creation')
        CLIENT_EDIT = 'CLIENT_EDIT', _('Client Modification')
        CLIENT_DELETE = 'CLIENT_DELETE', _('Client Deletion')
        SYSTEM_CONFIG = 'SYSTEM_CONFIG', _('System Configuration Change')

    admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='admin_actions'
    )
    action_type = models.CharField(
        max_length=20,
        choices=ActionTypes.choices
    )
    target_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_actions_against'
    )
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Admin Audit Log')
        verbose_name_plural = _('Admin Audit Logs')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['admin']),
            models.Index(fields=['action_type']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.admin} - {self.get_action_type_display()} at {self.timestamp}"

class SystemConfiguration(models.Model):
    """Stores system-wide configuration settings"""
    class ConfigTypes(models.TextChoices):
        GENERAL = 'GENERAL', _('General Settings')
        SECURITY = 'SECURITY', _('Security Settings')
        EMAIL = 'EMAIL', _('Email Settings')
        MAINTENANCE = 'MAINTENANCE', _('Maintenance Settings')

    config_type = models.CharField(
        max_length=20,
        choices=ConfigTypes.choices,
        default=ConfigTypes.GENERAL
    )
    key = models.CharField(max_length=100, unique=True)
    value = models.JSONField()
    description = models.TextField(blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        verbose_name = _('System Configuration')
        verbose_name_plural = _('System Configurations')
        ordering = ['config_type', 'key']
        constraints = [
            models.UniqueConstraint(
                fields=['config_type', 'key'],
                name='unique_config_key_per_type'
            )
        ]

    def __str__(self):
        return f"{self.get_config_type_display()}: {self.key}"

class BulkUserImportJob(models.Model):
    """Tracks bulk user import operations"""
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PROCESSING = 'PROCESSING', _('Processing')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')

    initiated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bulk_imports'
    )
    csv_file = models.FileField(upload_to='bulk_imports/')
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    total_records = models.PositiveIntegerField(default=0)
    successful = models.PositiveIntegerField(default=0)
    failed = models.PositiveIntegerField(default=0)
    error_log = models.TextField(blank=True)
    send_welcome_email = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Bulk User Import Job')
        verbose_name_plural = _('Bulk User Import Jobs')
        ordering = ['-started_at']

    def __str__(self):
        return f"Import #{self.id} - {self.get_status_display()}"

class AdminNotification(models.Model):
    """System notifications for administrators"""
    class SeverityLevels(models.TextChoices):
        INFO = 'INFO', _('Information')
        WARNING = 'WARNING', _('Warning')
        CRITICAL = 'CRITICAL', _('Critical')

    title = models.CharField(max_length=200)
    message = models.TextField()
    severity = models.CharField(
        max_length=10,
        choices=SeverityLevels.choices,
        default=SeverityLevels.INFO
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # THIS IS WHERE THE CORRECTED FIELD GOES:
    recipients = models.ManyToManyField(
        User,
        related_name='admin_notifications',
        limit_choices_to={'groups__name__in': ['SuperAdmin', 'ClientAdmin']}
    )

    class Meta:
        verbose_name = _('Admin Notification')
        verbose_name_plural = _('Admin Notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_read']),
            models.Index(fields=['severity']),
        ]

    def __str__(self):
        return f"{self.get_severity_display()}: {self.title}"

class SystemMaintenanceWindow(models.Model):
    """Scheduled system maintenance windows"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('System Maintenance Window')
        verbose_name_plural = _('System Maintenance Windows')
        ordering = ['-start_time']
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F('start_time')),
                name='end_time_after_start_time'
            )
        ]

    def __str__(self):
        return f"{self.title} ({self.start_time} to {self.end_time})"

    @property
    def is_currently_active(self):
        """Check if maintenance is currently active"""
        now = timezone.now()
        return self.is_active and self.start_time <= now <= self.end_time