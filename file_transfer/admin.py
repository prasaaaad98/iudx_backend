# file_transfer/admin.py

from django.contrib import admin
from .models import File, TransferHistory

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'original_owner', 'created_at', 'get_file_size']
    list_filter = ['created_at', 'owner', 'original_owner']
    search_fields = ['name', 'owner__username', 'original_owner__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('File Information', {
            'fields': ('name', 'file')
        }),
        ('Ownership', {
            'fields': ('owner', 'original_owner')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_file_size(self, obj):
        """Display file size in a readable format"""
        size = obj.get_file_size()
        if size < 1024:
            return f"{size} bytes"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    get_file_size.short_description = 'File Size'

@admin.register(TransferHistory)
class TransferHistoryAdmin(admin.ModelAdmin):
    list_display = ['file', 'action', 'from_user', 'to_user', 'timestamp']
    list_filter = ['action', 'timestamp', 'from_user', 'to_user']
    search_fields = ['file__name', 'from_user__username', 'to_user__username']
    readonly_fields = ['timestamp']
    
    fieldsets = (
        ('Transfer Information', {
            'fields': ('file', 'action', 'from_user', 'to_user')
        }),
        ('Additional Information', {
            'fields': ('notes', 'timestamp'),
            'classes': ('collapse',)
        }),
    )
