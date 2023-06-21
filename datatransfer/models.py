from django.db import models
from authentication.models import CustomUser


class Project(models.Model):
    project_name = models.CharField(max_length=30)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user')
    account_id = models.CharField(max_length=50, blank=True)
    filename_to_transfer = models.CharField(max_length=50, blank=True)
    date_create = models.DateField(auto_now_add=True)
    ssh_key = models.TextField(blank=True)
    ad_account_currency = models.CharField(blank=True, max_length=10)
    ga4_currency = models.CharField(blank=True, max_length=10)
    exchange_rate = models.FloatField(blank=True, default=1)
    upload_status = models.CharField(max_length=50, default='Success')

    def __str__(self):
        return self.project_name


class UploadHistory(models.Model):
    upload_date = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project')
    upload_status = models.CharField(max_length=50, default='Success')
    status_description = models.CharField(max_length=150)

    # def __str__(self):
    #     return self.pk
