from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.user_login, name='home'),
    path('logout/', views.user_logout, name='logout'),
    path('registration/', views.user_registration),
    path('raccount/', views.reg_permission, name='perm')
]