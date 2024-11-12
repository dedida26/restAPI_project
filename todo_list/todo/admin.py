from django.contrib import admin

from .models import Folder, Page, Task

admin.site.register(Folder)
admin.site.register(Page)
admin.site.register(Task)