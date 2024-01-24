from django.shortcuts import render
from rest_framework import generics
from authentication.models import CustomUser
from .serializers import CustomUserSerializer



# class UserListApi(generics.ListAPIView):
#     queryset = CustomUser.objects.all()
#     serializer_class = CustomUserSerializer



