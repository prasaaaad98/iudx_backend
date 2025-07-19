# file_transfer/views.py

from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes, parser_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from django.contrib.auth.models import User
from django.db.models import Q
from .models import File, TransferHistory
from .serializers import (
    FileSerializer, FileUploadSerializer, TransferSerializer,
    RevokeSerializer, TransferHistorySerializer
)

@api_view(['GET'])
def index(request):
    """API endpoint overview"""
    return Response({
        'message': 'File Transfer API is running',
        'version': '1.0.0',
        'endpoints': {
            'file_upload': '/api/upload/',
            'transfer': '/api/transfer/',
            'revoke': '/api/revoke/',
            'my_files': '/api/my-files/',
            'transfer_history': '/api/history/',
        },
        'user': request.user.username if request.user.is_authenticated else 'Anonymous'
    })

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
@renderer_classes([BrowsableAPIRenderer, JSONRenderer])
def upload_file(request):
    """Upload a new file"""
    if request.method == 'GET':
        # Return information about the upload endpoint for GET requests
        return Response({
            'message': 'File upload endpoint',
            'description': 'Upload files with ownership tracking',
            'required_fields': {
                'name': 'string - Name/description of the file',
                'file': 'file - The actual file to upload'
            },
            'method': 'POST',
            'content_type': 'multipart/form-data',
            'instructions': 'Use the HTML form below or switch to multipart/form-data in the dropdown'
        })
    
    # Handle POST request for file upload
    serializer = FileUploadSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        file_obj = serializer.save()
        return Response({
            'success': True,
            'message': 'File uploaded successfully',
            'file': FileSerializer(file_obj).data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'error': 'File upload failed',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
@renderer_classes([BrowsableAPIRenderer, JSONRenderer])
def transfer_file(request):
    """Transfer file ownership to another user"""
    serializer = TransferSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        result = serializer.save()
        return Response({
            'success': True,
            'message': result['message'],
            'file': FileSerializer(result['file']).data,
            'transfer_history': TransferHistorySerializer(result['transfer_history']).data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'error': 'Transfer failed',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
@renderer_classes([BrowsableAPIRenderer, JSONRenderer])
def revoke_file(request):
    """Revoke file transfer and return ownership to original owner"""
    serializer = RevokeSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        result = serializer.save()
        return Response({
            'success': True,
            'message': result['message'],
            'file': FileSerializer(result['file']).data,
            'transfer_history': TransferHistorySerializer(result['transfer_history']).data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'error': 'Revoke failed',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@renderer_classes([BrowsableAPIRenderer, JSONRenderer])
def my_files(request):
    """Get all files owned by the current user"""
    files = File.objects.filter(owner=request.user).order_by('-created_at')
    serializer = FileSerializer(files, many=True)
    return Response({
        'success': True,
        'count': files.count(),
        'files': serializer.data,
        'user': request.user.username
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@renderer_classes([BrowsableAPIRenderer, JSONRenderer])
def transfer_history(request):
    """Get transfer history for files involving the current user"""
    history = TransferHistory.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user)
    ).order_by('-timestamp')
    
    serializer = TransferHistorySerializer(history, many=True)
    return Response({
        'success': True,
        'count': history.count(),
        'history': serializer.data,
        'user': request.user.username
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    """List all users (helpful for finding user IDs for transfers)"""
    users = User.objects.filter(is_active=True).exclude(id=request.user.id)
    user_data = []
    for user in users:
        user_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        })
    
    return Response({
        'success': True,
        'message': 'Available users for file transfer',
        'current_user': {
            'id': request.user.id,
            'username': request.user.username
        },
        'available_users': user_data,
        'count': len(user_data)
    })

# Class-based views for additional functionality
class FileListView(generics.ListAPIView):
    """List all files for authenticated user with pagination support"""
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return File.objects.filter(owner=self.request.user).order_by('-created_at')

class FileDetailView(generics.RetrieveAPIView):
    """Get details of a specific file owned by the current user"""
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return File.objects.filter(owner=self.request.user)

class TransferHistoryListView(generics.ListAPIView):
    """List transfer history with pagination support"""
    serializer_class = TransferHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TransferHistory.objects.filter(
            Q(from_user=self.request.user) | Q(to_user=self.request.user)
        ).order_by('-timestamp')
