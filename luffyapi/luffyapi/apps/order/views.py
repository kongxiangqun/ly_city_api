from django.shortcuts import render
from rest_framework.generics import CreateAPIView
# Create your views here.
from . import models
from .serializers import OrderModelSerializer
from rest_framework.permissions import IsAuthenticated

class OrderView(CreateAPIView):
    queryset = models.Order.objects.filter(is_deleted=False,is_show=True)
    serializer_class = OrderModelSerializer
    permission_classes = [IsAuthenticated, ]
