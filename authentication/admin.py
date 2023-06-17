from itertools import count

from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'projects']
    search_fields = ['email']

    def projects(self, obj):
        return obj.user.count()


