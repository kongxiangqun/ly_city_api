from django.shortcuts import render

from . import models
# Create your views here.
from rest_framework.generics import ListAPIView,RetrieveAPIView
from .serializers import CourseCategoryModelSerializer, CourseModelsSerializer, CourseDetailModelSerializer, \
    CourseChapterModelSerializer
from .pagenations import StandardPageNumberPagination

from rest_framework.views import APIView
from rest_framework.response import Response

from django.conf import settings

class CategoryView(ListAPIView):

    queryset = models.CourseCategory.objects.filter(is_deleted=False,is_show=True)
    serializer_class = CourseCategoryModelSerializer


# class CourseView(ListAPIView):
#     queryset = models.Course.objects.filter(is_deleted=False,is_show=True).order_by('id')
#     serializer_class = CourseModelsSerializer


# 加过滤
class CourseView(ListAPIView):
    queryset = models.Course.objects.filter(is_deleted=False,is_show=True).order_by('id')
    serializer_class = CourseModelsSerializer
    filter_fields = ('course_category', )
    # 127.0.0.1/course/courses/?course_category=1
    pagination_class = StandardPageNumberPagination

class CourseDetailView(RetrieveAPIView):
    queryset = models.Course.objects.filter(is_deleted=False,is_show=True)
    serializer_class = CourseDetailModelSerializer


from django_filters.rest_framework import DjangoFilterBackend
class ChapterView(ListAPIView):
    queryset = models.CourseChapter.objects.filter(is_deleted=False,is_show=True)
    serializer_class = CourseChapterModelSerializer
    filter_backends = [DjangoFilterBackend,]
    filter_fields = ('course',)
    # /chapter/?course=1

from luffyapi.libs.polyv import PolyvPlayer
from rest_framework.permissions import IsAuthenticated


class PolyvView(APIView):
    # vid = '348e998797383060cb19620b1c600203_3'
    permission_classes = [IsAuthenticated, ]
    def get(self,request):
        polyv_obj = PolyvPlayer(settings.POLYV_CONF['userid'],settings.POLYV_CONF['secretKey'],settings.POLYV_CONF['tokenUrl'])
        vid = request.query_params.get('vid')
        viewerIp = request.META.get('REMOTE_ADDR')
        viewerId = request.user.id
        viewerName = request.user.username

        token_dict = polyv_obj.get_video_token(vid,viewerIp,viewerId,viewerName)

        return Response(token_dict)



