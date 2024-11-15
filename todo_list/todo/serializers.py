from rest_framework import serializers
from .models import *
from django.urls import reverse


class FolderPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolderPermission
        fields = ('id', 'folder', 'user', 'user_name', 'can_view', 'can_edit', 'can_delete')
        read_only_fields = ('id',)

    def get_user_name(self, obj):
        return obj.user.username

    user_name = serializers.SerializerMethodField()
    folder = serializers.PrimaryKeyRelatedField(queryset=Folder.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())


class PagePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagePermission
        fields = ('id', 'page', 'user', 'user_name', 'can_view', 'can_edit', 'can_delete')
        read_only_fields = ('id',)

    def get_user_name(self, obj):
        return obj.user.username

    user_name = serializers.SerializerMethodField()
    page = serializers.PrimaryKeyRelatedField(queryset=Page.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())


class TaskPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskPermission
        fields = ('id', 'task', 'user', 'user_name', 'can_view', 'can_edit', 'can_delete')
        read_only_fields = ('id',)

    def get_user_name(self, obj):
        return obj.user.username

    user_name = serializers.SerializerMethodField()
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())


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
            'folder': {'required': True}
        }

    folder = serializers.PrimaryKeyRelatedField(queryset=Folder.objects.all())
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
        fields = ('id', 'text', 'status', 'user', 'user_name', 'page', 'page_name', 'previous_version',
                  'previous_version_url', 'created_at', 'updated_at', 'created_by', 'updated_by')
        extra_kwargs = {
            'text': {'required': True},
            'page': {'required': True},
        }

    status = serializers.ChoiceField(choices=Task.STATUS_CHOICES)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True, format='%d-%m-%Y %H:%M:%S')
    updated_at = serializers.DateTimeField(read_only=True, format='%d-%m-%Y %H:%M:%S')
    page = serializers.PrimaryKeyRelatedField(queryset=Page.objects.all())
    user_name = serializers.SerializerMethodField()
    previous_version_url = serializers.SerializerMethodField()
    page_name = serializers.SerializerMethodField()

    def get_page_name(self, obj):
        return obj.page.name

    def get_user_name(self, obj):
        return obj.user.username

    def get_page_data(self, obj):
        page_serializer = PageSerializer(obj.page, fields=('id', 'name'))
        return page_serializer.data

    def get_previous_version_url(self, obj):
        if obj.previous_version:
            return reverse('task-detail', args=[obj.previous_version.id])
        return None
