from django.db.models import Q
from rest_framework import viewsets, permissions
from .serializers import *


class FolderViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    #  Авторизованные пользователи могут изменять данные
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    #  Дополнительные проверки прав в методах viewset
    def get_queryset(self):
        #  Получаем  список  папок  для  текущего  пользователя
        if self.request.user.is_authenticated:
            #  Проверяем,  имеет  ли  пользователь  права  на  просмотр  всех  папок
            if self.request.user.has_perm('todo.view_folder'):
                return Folder.objects.all()
            else:
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
            #  Проверяем,  имеет  ли  пользователь  права  на  просмотр  всех  страниц
            if self.request.user.has_perm('todo.view_page'):
                return Page.objects.all()
            else:
                return Page.objects.filter(Q(folder__owner=self.request.user) | Q(permissions__in=[self.request.user]) |
                                           Q(folder__is_public=True) | Q(is_public=True))
        else:
            return Page.objects.filter(is_public=True)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_authenticated:
            if self.request.user.has_perm('todo.view_task'):
                return queryset  # Возвращаем весь queryset, если есть право на все
            else:
                return queryset.filter(
                    Q(folder__owner=self.request.user) |
                    Q(permissions__in=[self.request.user]) |
                    Q(page__folder__is_public=True)
                )  # Фильтруем по правам, владельцу и публичным папкам
        else:
            return queryset.filter(page__folder__is_public=True)  # Возвращаем только публичные задачи для неавторизованных
