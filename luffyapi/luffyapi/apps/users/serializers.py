
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework import serializers
from rest_framework_jwt.compat import get_username_field, PasswordField
from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate, get_user_model
from rest_framework_jwt.settings import api_settings
User = get_user_model()
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER

from . import models
import re
from django.contrib.auth.hashers import make_password
from .utils import get_user_obj

from django_redis import get_redis_connection

from order.models import Order

class CustomeSerializer(JSONWebTokenSerializer):

    def __init__(self, *args, **kwargs):
        """
        Dynamically add the USERNAME_FIELD to self.fields.
        """
        super(JSONWebTokenSerializer, self).__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = PasswordField(write_only=True)

        self.fields['ticket'] = serializers.CharField(write_only=True) # 必须要给我
        self.fields['randstr'] = serializers.CharField(write_only=True)

    # 修改校验功能 先把它的validate全局钩子拿过来
    def validate(self, attrs):
        credentials = {
            # 用户名和密码都是在我们utils中拿的
            self.username_field: attrs.get(self.username_field),
            'password': attrs.get('password'),
            # 还需要啊传递这两个额外参数
            'ticket': attrs.get('ticket'),
            'randstr': attrs.get('randstr'),
        }
        #{'username':'root',password:'123'}

        if all(credentials.values()):

            user = authenticate(self.context['request'],**credentials)  #self.context['request']当前请求的request对象

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg)

                payload = jwt_payload_handler(user)

                return {
                    'token': jwt_encode_handler(payload),
                    'user': user
                }
            else:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "{username_field}" and "password".')
            msg = msg.format(username_field=self.username_field)
            raise serializers.ValidationError(msg)

class RegisterModelSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    # 指定的model表中没有这个字段,但是还要校验这个字段
    # 不序列化但要反序列化校验
    sms = serializers.CharField(max_length=6, min_length=4, write_only=True)  # '3333'
    r_password = serializers.CharField(write_only=True)
    # 点击注册时浏览器不需要传给我,但是序列化是我需要给浏览器
    token = serializers.CharField(read_only=True)  #

    class Meta:
        model = models.User
        # phone password r_password
        # sms 验证码\r_password 重复密码\token 字段User表中没有写在上面,但要在这里指定一下
        fields = ['id', 'phone', 'password', 'r_password', 'sms', 'token']
        # 数据库中有这个password字段,不需要再上面重新声明
        extra_kwargs = {
            'password': {'write_only': True},
        }
        # 很多网站注册的时候,手机号直接注册成功,登陆成功的用户名就是手机号,我们这个也这样

    # ****************** 校验 **********************

    # 校验密码和确认密码
    def validate(self, attrs):
        # 校验手机号 因为前段可能没走onbule事件,直接通过requests发送数据
        print('>>>>',attrs)
        phone_number = attrs.get('phone')
        sms = attrs.get('sms')
        if not re.match('^1[3-9][0-9]{9}$', phone_number):
            raise serializers.ValidationError('手机号格式不对')
        # 校验唯一性
        ret = get_user_obj(phone_number)
        if ret:
            raise serializers.ValidationError('手机号已被注册')

        # 校验密码和确认密码
        p1 = attrs.get('password')
        p2 = attrs.get('r_password')
        if p1 != p2:
            raise serializers.ValidationError('两次密码不一致，请核对')

        # todo  校验验证码
        conn = get_redis_connection('sms_code')
        ret = conn.get('mobile_%s'%phone_number)
        if not ret:
            raise serializers.ValidationError('验证码已失效')
        if ret.decode() != sms:
            raise serializers.ValidationError('验证码输入有误')

        return attrs
    # ******************* 校验结束 *****************
    # ******************* 保存数据 *****************

    # 用户提交过来的数据包括[手机验证码,密码,确认密码,手机号],验证码和确认密码是不用存的
    # 调用save方法时,自动触发执行create方法
    def create(self, validated_data):
        # 剔除 确认密码
        validated_data.pop('r_password')
        # 剔除 手机验证码
        validated_data.pop('sms')
        # 密码是要加密后才能保存
        # User表是怎么加密的,继承的AbstracUser,提供方法
        hash_password = make_password(validated_data['password'])
        validated_data['password'] = hash_password
        #
        validated_data['username'] = validated_data.get('phone')
        user = models.User.objects.create(
            **validated_data
        )


        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        # user.token = '123'
        user.token = token
        # return 的 就是反序列化后保存数据,在序列化这个对象的结果返回
        return user



class MyOrderModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'order_number' ,'pay_time', 'get_order_status_display', 'order_detail_data']

