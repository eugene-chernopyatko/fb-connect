from django.db import models
from authentication.models import CustomUser


class Project(models.Model):
    project_name = models.CharField(max_length=30)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user')
    account_id = models.CharField(max_length=50, blank=True)
    filename_to_transfer = models.CharField(max_length=50, blank=True)
    date_create = models.DateField(auto_now_add=True)
    ssh_key = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.project_name