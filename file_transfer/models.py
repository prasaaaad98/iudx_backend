# file_transfer/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os

class File(models.Model):
    """
    Model to store file information and track ownership
    """
    name = models.CharField(max_length=255, help_text="Name of the file")
    file = models.FileField(upload_to='uploads/', help_text="The actual file upload")
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='owned_files',
        help_text="Current owner of the file"
    )
    original_owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='originally_owned_files',
        help_text="Original owner of the file (for revoke functionality)"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the file was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="When the file was last updated")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "File"
        verbose_name_plural = "Files"
    
    def __str__(self):
        return f"{self.name} (Owner: {self.owner.username})"
    
    def get_file_size(self):
        """Return file size in bytes"""
        if self.file:
            return self.file.size
        return 0
    
    def get_file_extension(self):
        """Return file extension"""
        if self.file:
            return os.path.splitext(self.file.name)[1]
        return ""

class TransferHistory(models.Model):
    """
    Model to track all transfer and revoke actions for audit purposes
    """
    ACTION_CHOICES = [
        ('TRANSFER', 'Transfer'),
        ('REVOKE', 'Revoke'),
    ]
    
    file = models.ForeignKey(
        File, 
        on_delete=models.CASCADE, 
        related_name='transfer_history',
        help_text="Reference to the file being transferred"
    )
    from_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='transfers_from',
        help_text="User transferring the file"
    )
    to_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='transfers_to',
        help_text="User receiving the file"
    )
    action = models.CharField(
        max_length=10, 
        choices=ACTION_CHOICES,
        help_text="Type of action performed"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the action occurred"
    )
    notes = models.TextField(
        blank=True, 
        null=True,
        help_text="Additional notes about the transfer"
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Transfer History"
        verbose_name_plural = "Transfer Histories"
    
    def __str__(self):
        return f"{self.action}: {self.file.name} from {self.from_user.username} to {self.to_user.username}"
    
    @property
    def is_transfer(self):
        return self.action == 'TRANSFER'
    
    @property
    def is_revoke(self):
        return self.action == 'REVOKE'
