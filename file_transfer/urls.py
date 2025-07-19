# file_transfer/urls.py

from django.urls import path
from . import views

app_name = 'file_transfer'

urlpatterns = [
    # API overview
    path('', views.index, name='index'),
    
    # File management
    path('upload/', views.upload_file, name='upload_file'),
    path('my-files/', views.my_files, name='my_files'),
    path('files/', views.FileListView.as_view(), name='file_list'),
    path('files/<int:pk>/', views.FileDetailView.as_view(), name='file_detail'),
    
    # Transfer operations
    path('transfer/', views.transfer_file, name='transfer_file'),
    path('revoke/', views.revoke_file, name='revoke_file'),
    
    # History and user management
    path('history/', views.transfer_history, name='transfer_history'),
    path('users/', views.list_users, name='list_users'),  # New endpoint
]
