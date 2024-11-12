from django.db.models import Q
from .models import *
from rest_framework import viewsets, permissions
from .serializers import (FolderSerializer, PageSerializer, TaskSerializer)


class FolderViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    #  Авторизованные пользователи могут изменять данные
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    #  Дополнительные проверки прав в методах viewset
    def get_queryset(self):
        #  Получаем список папок для текущего пользователя
        if self.request.user.is_authenticated:
            return Folder.objects.filter(Q(owner=self.request.user) | Q(permissions__in=[self.request.user]) |
                                         Q(is_public=True))
        else:
            return Folder.objects.filter(is_public=True)


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Page.objects.filter(Q(folder__owner=self.request.user) | Q(permissions__in=[self.request.user]) |
                                       Q(folder__is_public=True) | Q(is_public=True))
        else:
            return Page.objects.filter(is_public=True)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Task.objects.filter(Q(folder__owner=self.request.user) | Q(permissions__in=[self.request.user]) |
                                       Q(folder__is_public=True) | Q(page__is_public=True))
        else:
            return Task.objects.filter(page__is_public=True)
