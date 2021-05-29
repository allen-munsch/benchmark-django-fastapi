import os
import json

from django.shortcuts import render

# Create your views here.
from .models import ClownCollege, Troupe
from django.http import HttpResponse
from asgiref.sync import sync_to_async
from djantic import ModelSchema

class ClownCollegeSchema(ModelSchema):
    class Config:
        model = ClownCollege

class TroupeSchema(ModelSchema):
    class Config:
        model = Troupe

async def clowncollege_with_django_async_orm(request, *args, **kwargs):
    cc = ClownCollegeSchema.from_django(await ClownCollege.objects.prefetch_related('troupe').async_all(), many=True)
    data = [item.json() for item in cc]
    j = {"results": data, "count": len(data), "next": "stubbed"}
    return HttpResponse(json.dumps(j), content_type='application/json')

def clowncollege(request, *args, **kwargs):
    # if os.environ['test_with_slowapi']:
    #     cc = sync_to_async(ClownCollegeSchema.from_django)(ClownCollege.objects.all(), many=True)
    # else:
    #     cc = ClownCollegeSchema.from_django(ClownCollege.objects.all(), many=True)
    # data = [item.json() for item in cc]
    j = {"results": ['blah'], "count": len(['blah']), "next": "stubbed"}
    return HttpResponse(json.dumps(j), content_type='application/json')

def troupe(request, *args, **kwargs):
    # t = TroupeSchema.from_django(Troupe.objects.all(), many=True)
    # data = [item.json() for item in t]
    j = {"results": ['blah'], "count": len(['blah']), "next": "stubbed"}
    return HttpResponse(json.dumps(j), content_type='application/json')

@sync_to_async
def get_all_clowns():
    return ClownCollegeSchema.from_django(ClownCollege.objects.all(), many=True)

@sync_to_async
def get_all_troupes():
    return TroupeSchema.from_django(Troupe.objects.all(), many=True)

async def async_clowncollege(request, *args, **kwargs):
    cc = await get_all_clowns()
    data = [item.json() for item in cc]
    j = {"results": data, "count": len(data), "next": "stubbed"}
    return HttpResponse(json.dumps(j), content_type='application/json')

async def async_troupe(request, *args, **kwargs):
    t = await get_all_troupes()
    data = [item.json() for item in t]
    j = {"results": data, "count": len(data), "next": "stubbed"}
    return HttpResponse(json.dumps(j), content_type='application/json')
