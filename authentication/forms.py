from django import forms
from django.forms import TextInput

from .models import CustomUser


class RegistrationUserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.label = ""

    class Meta:
        model = CustomUser
        fields = ['email', 'password']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Email"}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
        }


class UserLoginForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.label = ""

    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email',
                                                           'id': 'email-login'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password',
                                                                 'id': 'password-login'}))


class PermissionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.label = ""

    class Meta:
        model = CustomUser
        fields = ['fb_app_id', 'fb_account_secret', 'fb_access_token']
        widgets = {
            'fb_app_id': TextInput(attrs={'class': 'form-control', 'placeholder': "Facebook App Id"}),
            'fb_account_secret': TextInput(attrs={'class': 'form-control', 'placeholder': "Facebook App Secret"}),
            'fb_access_token': TextInput(attrs={'class': 'form-control', 'placeholder': "Facebook Access Token"})
        }

