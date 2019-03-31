from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import generics
from rest_framework import status
from toys.models import Toy
from toys.serializers import ToySerializer

# Create your views here.
class ToyListView(generics.ListCreateAPIView):
    queryset = Toy.objects.all()
    serializer_class = ToySerializer

class ToyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Toy.objects.all()
    serializer_class = ToySerializer
