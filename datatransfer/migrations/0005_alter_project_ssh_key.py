# Generated by Django 4.2.2 on 2023-06-15 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datatransfer', '0004_project_ssh_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='ssh_key',
            field=models.TextField(blank=True),
        ),
    ]
