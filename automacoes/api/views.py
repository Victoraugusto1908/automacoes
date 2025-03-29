from django.shortcuts import render

# Create your views here.
# api/views.py
from django.http import HttpResponse

def hello_view(request):
    return HttpResponse("Hello, world!")
