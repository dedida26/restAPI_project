from rest_framework import serializers
from .models import *
from django.urls import reverse


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ('id', 'name', 'owner', 'owner_name', 'is_public')
        extra_kwargs = {
            'owner': {'read_only': True},
            'owner_name': {'read_only': True}
        }

    name = serializers.CharField(max_length=255)
    owner_name = serializers.SerializerMethodField()

    def get_owner_name(self, obj):
        return obj.owner.username


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('id', 'name', 'folder', 'folder_data', 'is_public', 'created_at',
                  'updated_at', 'created_by', 'updated_by')
        extra_kwargs = {
            'name': {'required': True},
            'folder': {'read_only': True, 'required': True}
        }

    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)
    folder_data = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True, format='%d-%m-%Y %H:%M:%S')
    updated_at = serializers.DateTimeField(read_only=True, format='%d-%m-%Y %H:%M:%S')

    def get_folder_data(self, obj):
        folder_serializer = FolderSerializer(instance=obj.folder)
        return folder_serializer.data


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'text', 'status', 'user', 'user_name', 'folder', 'previous_version', 'previous_version_url',
                  'page', 'created_at', 'updated_at', 'created_by', 'updated_by')
        extra_kwargs = {
            'text': {'required': True},
            'page': {'read_only': True, 'required': True},
            'previous_version': {'read_only': True},
        }

    status = serializers.ChoiceField(choices=Task.STATUS_CHOICES)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True, format='%d-%m-%Y %H:%M:%S')
    updated_at = serializers.DateTimeField(read_only=True, format='%d-%m-%Y %H:%M:%S')
    page = PageSerializer(read_only=True)
    user_name = serializers.SerializerMethodField()
    previous_version_url = serializers.SerializerMethodField()

    def get_user_name(self, obj):
        return obj.user.username

    def get_page_data(self, obj):
        page_serializer = PageSerializer(obj.folder, fields=('id', 'name'))
        return page_serializer.data

    def get_previous_version_url(self, obj):
        if obj.previous_version:
            return reverse('task-detail', args=[obj.previous_version.id])
        return None
