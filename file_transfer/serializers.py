# file_transfer/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import File, TransferHistory
import os

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class FileSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    original_owner = UserSerializer(read_only=True)
    file_size = serializers.SerializerMethodField()
    file_extension = serializers.SerializerMethodField()
    
    class Meta:
        model = File
        fields = ['id', 'name', 'file', 'owner', 'original_owner', 
                 'created_at', 'updated_at', 'file_size', 'file_extension']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_file_size(self, obj):
        return obj.get_file_size()
    
    def get_file_extension(self, obj):
        return obj.get_file_extension()

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['name', 'file']
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['owner'] = user
        validated_data['original_owner'] = user
        return super().create(validated_data)

class TransferSerializer(serializers.Serializer):
    file_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()
    
    def validate_file_id(self, value):
        try:
            file_obj = File.objects.get(id=value)
            if file_obj.owner != self.context['request'].user:
                raise serializers.ValidationError("You can only transfer files you own.")
            return value
        except File.DoesNotExist:
            raise serializers.ValidationError("File not found.")
    
    def validate_to_user_id(self, value):
        try:
            User.objects.get(id=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Recipient user not found.")
    
    def validate(self, data):
        if data['to_user_id'] == self.context['request'].user.id:
            raise serializers.ValidationError("You cannot transfer a file to yourself.")
        return data
    
    def create(self, validated_data):
        file_obj = File.objects.get(id=validated_data['file_id'])
        to_user = User.objects.get(id=validated_data['to_user_id'])
        from_user = self.context['request'].user
        
        file_obj.owner = to_user
        file_obj.save()
        
        transfer_history = TransferHistory.objects.create(
            file=file_obj,
            from_user=from_user,
            to_user=to_user,
            action='TRANSFER'
        )
        
        return {
            'file': file_obj,
            'transfer_history': transfer_history,
            'message': f'File "{file_obj.name}" successfully transferred to {to_user.username}'
        }

class RevokeSerializer(serializers.Serializer):
    file_id = serializers.IntegerField()
    
    def validate_file_id(self, value):
        try:
            file_obj = File.objects.get(id=value)
            if file_obj.original_owner != self.context['request'].user:
                raise serializers.ValidationError("Only the original owner can revoke file transfers.")
            
            if file_obj.owner == file_obj.original_owner:
                raise serializers.ValidationError("This file has not been transferred and cannot be revoked.")
            
            return value
        except File.DoesNotExist:
            raise serializers.ValidationError("File not found.")
    
    def create(self, validated_data):
        file_obj = File.objects.get(id=validated_data['file_id'])
        current_owner = file_obj.owner
        original_owner = file_obj.original_owner
        
        file_obj.owner = original_owner
        file_obj.save()
        
        revoke_history = TransferHistory.objects.create(
            file=file_obj,
            from_user=current_owner,
            to_user=original_owner,
            action='REVOKE'
        )
        
        return {
            'file': file_obj,
            'transfer_history': revoke_history,
            'message': f'File "{file_obj.name}" ownership revoked and returned to {original_owner.username}'
        }

class TransferHistorySerializer(serializers.ModelSerializer):
    file = FileSerializer(read_only=True)
    from_user = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)
    
    class Meta:
        model = TransferHistory
        fields = ['id', 'file', 'from_user', 'to_user', 'action', 'timestamp', 'notes']
