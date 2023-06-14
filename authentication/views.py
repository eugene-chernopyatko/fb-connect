from django.http import HttpResponse
from django.shortcuts import render
from .models import CustomUser
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from .forms import RegistrationUserForm, UserLoginForm, PermissionForm


def user_registration(request):
    if request.method == 'POST':
        form = RegistrationUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            user.password = make_password(password)
            user.save()
            return redirect('home')
    form = RegistrationUserForm()
    return render(request, 'user_registration.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('projects')
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                return redirect('projects')
            else:
                form.add_error(None, 'Invalid username or password.')
                return render(request, 'index.html', {'form': form, 'error': form.errors})
    else:
        form = UserLoginForm()
        return render(request, 'index.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')


def reg_permission(request):
    if request.method == 'POST':
        user = CustomUser.objects.get(pk=request.user.pk)
        user.fb_app_id = request.POST['fb_app_id']
        user.fb_account_secret = request.POST['fb_account_secret']
        user.fb_access_token = request.POST['fb_access_token']
        user.save()
        return redirect('projects')

    else:
        form = PermissionForm(initial={'fb_app_id': request.user.fb_app_id,
                                       'fb_account_secret': request.user.fb_account_secret,
                                       'fb_access_token': request.user.fb_access_token})
        return render(request, 'account_permissions.html', {'form': form})

