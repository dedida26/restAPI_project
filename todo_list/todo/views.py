from django.db.models import Q
from rest_framework import viewsets, permissions, status
from .serializers import *
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class SoftDeletableViewSetMixin:

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class FolderViewSet(SoftDeletableViewSetMixin, viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Помечаем папку как удаленную
        instance.is_deleted = True
        instance.save()

        # "Мягко" удаляем страницы в папке
        for page in instance.page_set.all():
            page.is_deleted = True
            page.save()

        # "Мягко" удаляем задачи в папке
        for task in Task.objects.filter(page__in=instance.page_set.all()).filter(is_deleted=False):
            task.is_deleted = True
            task.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            # Фильтруем только если пользователь авторизован
            return Folder.objects.filter(
                Q(owner=user) | Q(permissions__in=[user]) | Q(is_public=True)
            ).filter(is_deleted=False).distinct()  # Добавлен фильтр is_deleted=False
        else:
            # Для неавторизованных пользователей возвращаем только публичные папки
            return Folder.objects.filter(is_public=True, is_deleted=False).distinct()


class PageViewSet(SoftDeletableViewSetMixin, viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        folder = serializer.validated_data['folder']
        user = self.request.user

        # Проверка прав доступа
        if not (folder.owner == user or user in folder.permissions.all()):
            raise PermissionDenied("У вас нет прав на создание страницы в этой папке.")

        serializer.save(created_by=user, updated_by=user)

    def get_queryset(self):
        user = self.request.user

        if user.has_perm('todo.view_page'):
            return Page.objects.all().filter(is_deleted=False)

        if user.is_authenticated:
            return Page.objects.filter(
                Q(folder__owner=user) |
                Q(folder__permissions__in=[user]) |
                Q(is_public=True)
            ).filter(is_deleted=False).distinct()
        else:
            return Page.objects.filter(is_public=True, is_deleted=False).distinct()


class TaskViewSet(SoftDeletableViewSetMixin, viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        page_id = self.request.data.get('page')
        if not page_id:
            raise serializers.ValidationError({"page": "Требуется ID страницы"})

        try:
            page = Page.objects.get(pk=page_id)
        except Page.DoesNotExist:
            raise serializers.ValidationError({"page": "Страница не найдена"})

        user = self.request.user

        # Проверка прав доступа к странице и папке
        if not (page.folder.owner == user or user in page.folder.permissions.all() or page.is_public):
            raise PermissionDenied("У вас нет прав на создание задачи на этой странице.")

        serializer.save(created_by=user, updated_by=user, page=page)

    def get_queryset(self):
        user = self.request.user

        if user.has_perm('todo.view_task'):
            return Task.objects.all().filter(is_deleted=False)

        if user.is_authenticated:
            return Task.objects.filter(
                Q(page__folder__owner=user) |
                Q(page__folder__permissions__in=[user]) |
                Q(page__is_public=True)
            ).filter(is_deleted=False).distinct()
        else:
            return Task.objects.filter(page__is_public=True, is_deleted=False, page__is_deleted=False).distinct()


class FolderPermissionViewSet(viewsets.ModelViewSet):
    queryset = FolderPermission.objects.all()
    serializer_class = FolderPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(folder__owner=user)

    def perform_create(self, serializer):
        folder = serializer.validated_data.get('folder')
        user_to_grant = serializer.validated_data.get('user')
        if folder.owner != self.request.user:
            raise serializers.ValidationError("Вы не можете назначать права для этой папки.")
        serializer.save()

    def perform_destroy(self, instance):
        folder = instance.folder
        if folder.owner != self.request.user:
            raise serializers.ValidationError("Вы не можете удалить права для этой папки.")
        instance.delete()


class PagePermissionViewSet(viewsets.ModelViewSet):
    queryset = PagePermission.objects.all()
    serializer_class = PagePermissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return PagePermission.objects.filter(page__folder__owner=user) | PagePermission.objects.filter(
            page__permissions__in=[user]) | PagePermission.objects.filter(page__is_public=True)

    def perform_create(self, serializer):
        page = serializer.validated_data.get('page')
        user_to_grant = serializer.validated_data.get('user')
        if page.folder.owner != self.request.user and not page.folder.permissions.filter(
                pk=self.request.user.pk).exists():
            raise serializers.ValidationError(
                "Вы не можете назначать права для этой страницы."
            )
        serializer.save()


class TaskPermissionViewSet(viewsets.ModelViewSet):
    queryset = TaskPermission.objects.all()
    serializer_class = TaskPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return TaskPermission.objects.filter(
            task__page__folder__owner=user
        ) | TaskPermission.objects.filter(
            task__page__permissions__in=[user]
        ) | TaskPermission.objects.filter(
            task__page__is_public=True
        )

    def perform_create(self, serializer):
        task = serializer.validated_data.get('task')
        user_to_grant = serializer.validated_data.get('user')
        if task.page.folder.owner != self.request.user and not task.page.folder.permissions.filter(
                pk=self.request.user.pk).exists():
            raise serializers.ValidationError("Вы не можете назначать права для этой задачи.")
        serializer.save()
