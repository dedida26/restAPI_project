from django.db import models
from django.contrib.auth.models import User


class FolderPermission(models.Model):
    folder = models.ForeignKey('Folder', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    can_view = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('folder', 'user')


class PagePermission(models.Model):
    page = models.ForeignKey('Page', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    can_view = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('page', 'user')


class TaskPermission(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    can_view = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('task', 'user')


class Folder(models.Model):
    name = models.CharField(unique=True, max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folder_owner')
    is_public = models.BooleanField(default=False)
    permissions = models.ManyToManyField(User, through='FolderPermission', blank=True,
                                         related_name='folder_permissions')

    def __str__(self):
        return self.name


class Page(models.Model):
    name = models.CharField(unique=True, max_length=50)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_page')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_page')
    permissions = models.ManyToManyField(User, through='PagePermission', blank=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    text = models.TextField(max_length=255)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    STATUS_CHOICES = (
        ('DONE', 'Выполнено'),
        ('IN_PROGRESS', 'В процессе'),
        ('CANCELLED', 'Отменено'),
    )
    status = models.CharField(choices=STATUS_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_task')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_task')
    previous_version = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    permissions = models.ManyToManyField(User, through='TaskPermission', blank=True, related_name='task_permissions')

    def __str__(self):
        return self.text
