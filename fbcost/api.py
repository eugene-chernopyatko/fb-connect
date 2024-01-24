import time

from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Schema, ModelSchema
from typing import List
from authentication.models import CustomUser
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict, ValidationError, BaseModel

from ninja import Router

api = NinjaAPI()


class A(ModelSchema):
    class Config:
        model = CustomUser
        model_fields = ['id','email', 'password']


@api.get("/users", response=List[A])
def hello(request):
    qs = CustomUser.objects.all()
    time.sleep(10)
    return qs


@api.get('/users/{a}', response=A)
def get_user(request, a: int):
    qs = get_object_or_404(CustomUser, pk=a)
    return qs


@api.post('/b')
def create(request, payload: A):
    print(payload.dict())
    user = CustomUser.objects.create(**payload.dict())
    return {'id': user.id}
