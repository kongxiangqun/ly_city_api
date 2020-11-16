import random
import re

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
# Create your views here.
from rest_framework_jwt.views import ObtainJSONWebToken
from rest_framework import status
from users.serializers import CustomeSerializer, RegisterModelSerializer, MyOrderModelSerializer
from .utils import get_user_obj
from . import models
from luffyapi.settings import contains

from rest_framework.generics import ListAPIView
from order.models import Order
from rest_framework.permissions import IsAuthenticated

class MyOrderView(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = MyOrderModelSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

# 验证码
from luffyapi.libs.ronglian_sms_sdk.sms import send_message
from django.conf import settings

class CustomLoginView(ObtainJSONWebToken):
    serializer_class = CustomeSerializer

# 后台对手机号进行简单的逻辑判断 引用APIView
class CheckPhoneNumber(APIView):

    def get(self,request):
        # 获取前端传过来的手机号
        phone_number = request.GET.get('phone')
        # 校验 后台校验为了爬虫通过requests发请求,后台不校验就跨过了手机号直接登录了
        if not re.match('^1[3-9][0-9]{9}$', phone_number):
            # 校验失败,格式不对 Response 返回接口数据
            # 返回状态码是因为DRF Response都是 200 错误信息都在前端的.then中
            # 返回400就是为了错误的在catch中处理
            return Response({'error_msg':'手机号格式有误，请重新输入！'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证唯一性,在数据库中没查到,才说明是新用户
        # 在utils中get_user_obj做了用户名或手机号在数据库中能否查到
        ret = get_user_obj(phone_number)
        if ret:
            return Response({'error_msg': '手机号已被注册，请换手机号'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'msg': 'ok'})

# 短信 打印日志
import logging
logger = logging.getLogger('django')


# 如果继承的是APIView get方法要自己写,数据的保存校验也要自己写
# 视图CreateAPIView 保存记录 定义了post CreateModelMixin 序列化保存
class RegisterView(CreateAPIView):
    queryset = models.User.objects.all()
    serializer_class = RegisterModelSerializer


from django_redis import get_redis_connection
class GetSMSCodeView(APIView):

    def get(self,request,phone):
        # 验证是否已经发送过短信了
        conn = get_redis_connection('sms_code')
        ret = conn.get('mobile_interval_%s'%phone)

        if ret:
            return Response({'msg':'60秒内已经发送过了，别瞎搞'}, status=status.HTTP_400_BAD_REQUEST)

        # 生成验证码 如果生成的数字小于6位, %06d 用0给补到6位
        sms_code = "%06d" % random.randint(0,999999)

        # 保存验证码
        # 设置键值 过期时间
        # 设置有效期
        conn.setex('mobile_%s'%phone, contains.SMS_CODE_EXPIRE_TIME, sms_code)

        # 设置发送短信的时间间隔
        conn.setex('mobile_interval_%s'%phone, contains.SMS_CODE_INTERVAL_TIME, sms_code)


        #todo 发送验证码 同步的交给celery
        # ret = send_message(settings.SMS_INFO.get('TID'), phone, (sms_code,contains.SMS_CODE_EXPIRE_TIME // 60))
        # if not ret:
        #     logger.error('{}手机号短信发送失败'.format(phone))
        #     return Response({"msg":'短信发送失败,请联系管理员'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        from celery.result import AsyncResult
        from mycelery.sms.tasks import sms_codes

        # ret = sms_codes.delay(phone, sms_code)
        sms_codes.delay(phone, sms_code)
        # async_task = AsyncResult(id=ret.id,app=sms_codes)
        # result = async_task.get()
        # print('xxx',result) # xxx 短信发送成功啦^-^

        return Response({'msg':'ok'})