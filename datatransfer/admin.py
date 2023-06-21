from django.contrib import admin
from .models import Project, UploadHistory
# Register your models here.


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'project_name', 'user']
    search_fields = ['project_name']


admin.site.register(UploadHistory)