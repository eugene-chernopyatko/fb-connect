# Generated by Django 4.2.2 on 2023-06-17 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datatransfer', '0005_alter_project_ssh_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='ad_account_currency',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name='project',
            name='exchange_rate',
            field=models.FloatField(blank=True, default=1),
        ),
        migrations.AddField(
            model_name='project',
            name='ga4_currency',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]