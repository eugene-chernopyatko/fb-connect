from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.projects_main, name='projects'),
    path('go/', views.go),
    path('<int:pk>', views.get_project, name='project-detail'),
    path('create/', views.create_project, name='create-project')
]