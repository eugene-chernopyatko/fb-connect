import paramiko

from .models import Project
from django.forms import ModelForm, Textarea, TextInput
from django import forms


class CreateProjectForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.label = ""

    class Meta:
        model = Project
        fields = ['project_name']
        widgets = {
            'project_name': TextInput(attrs={'class': 'form-control', 'placeholder': "Project Name"})}

    def clean_project_name(self):
        project_name = self.cleaned_data['project_name']
        if ' ' in project_name:
            raise forms.ValidationError('Project name must not contain spaces')
        return project_name


class ProjectOpenKeyForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.label = ""

    class Meta:
        model = Project
        fields = ['ssh_key']
        widgets = {
            'ssh_key': TextInput(attrs={'class': 'form-control', 'placeholder': "Paste key here!"})}

    def clean_ssh_key(self):
        ssh_key = self.cleaned_data['ssh_key']
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname='ssh.pythonanywhere.com', username='neyokee', password='kscfrjdf2686991')
        sftp = ssh.open_sftp()
        remote_file_path = '/home/neyokee/.ssh/authorized_keys'
        with sftp.open(remote_file_path) as file:
            file_content = file.readlines()

        for i in file_content:
            if i == ssh_key:
                raise forms.ValidationError('This key is already authorized')
        return ssh_key
