import json

from django.shortcuts import render

# Create your views here.
from .models import ClownCollege, Troupe
from django.http import HttpResponse

from djantic import ModelSchema

class ClownCollegeSchema(ModelSchema):
    class Config:
        model = ClownCollege

class TroupeSchema(ModelSchema):
    class Config:
        model = Troupe

def clowncollege(request, *args, **kwargs):
    cc = ClownCollegeSchema.from_django(ClownCollege.objects.all(), many=True)
    data = [item.json() for item in cc]
    j = {"results": data, "count": len(data), "next": "stubbed"}
    return HttpResponse(json.dumps(j), content_type='application/json')

def troupe(request, *args, **kwargs):
    t = TroupeSchema.from_django(Troupe.objects.all(), many=True)
    data = [item.json() for item in t]
    j = {"results": data, "count": len(data), "next": "stubbed"}
    return HttpResponse(json.dumps(j), content_type='application/json')
