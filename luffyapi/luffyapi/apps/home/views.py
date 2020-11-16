from django.shortcuts import render
from rest_framework.generics import ListAPIView
# Create your views here.
from luffyapi.settings import contains
from . import models
from .serializers import BannerModelSerializer,NavModelSerializer


class BannerView(ListAPIView):
    queryset = models.Banner.objects.filter(is_deleted=False,is_show=True)[0:contains.BANNER_LENGTH]
    serializer_class = BannerModelSerializer


class NavView(ListAPIView):
    """
    导航栏接口
    """
    # position=1获取顶部导航栏数据
    queryset = models.Nav.objects.filter(is_deleted=False,is_show=True,position=1)[0:contains.NAV_TOP_LENGTH]
    serializer_class = NavModelSerializer


