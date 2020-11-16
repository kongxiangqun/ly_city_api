from django.shortcuts import render
import datetime
from rest_framework.views import APIView
# Create your views here.
from alipay import AliPay, DCAliPay, ISVAliPay
from alipay.utils import AliPayConfig
from django.conf import settings
from rest_framework.response import Response
from order.models import Order

from users.models import User, UserCourse
from course.models import CourseExpire
from rest_framework import status
from coupon.models import UserCoupon
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django_redis import get_redis_connection
import logging

logger = logging.getLogger('django')

class AlipayView(APIView):

    def get(self, request):
        order_number = request.query_params.get('order_number')
        order_obj = Order.objects.get(order_number=order_number)


        alipay = AliPay(
            appid=settings.ALIAPY_CONFIG['appid'],
            app_notify_url=None,  # 默认回调url
            app_private_key_string=open(settings.ALIAPY_CONFIG['app_private_key_path']).read(),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=open(settings.ALIAPY_CONFIG['alipay_public_key_path']).read(),
            sign_type=settings.ALIAPY_CONFIG['sign_type'],  # RSA 或者 RSA2
            debug = settings.ALIAPY_CONFIG['debug'],  # 默认False
        )

        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_obj.order_number,
            # out_trade_no=20161113,
            total_amount=float(order_obj.real_price),
            subject=order_obj.order_title,
            return_url=settings.ALIAPY_CONFIG['return_url'],
            notify_url=settings.ALIAPY_CONFIG['notify_url'] # 可选, 不填则使用默认notify url
        )

        url = settings.ALIAPY_CONFIG['gateway_url'] + order_string

        return Response({'url': url})



class AlipayResultView(APIView):
    permission_classes = [IsAuthenticated, ]
    def get(self,request):
        alipay = AliPay(
            appid=settings.ALIAPY_CONFIG['appid'],
            app_notify_url=None,  # 默认回调url
            app_private_key_string=open(settings.ALIAPY_CONFIG['app_private_key_path']).read(),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=open(settings.ALIAPY_CONFIG['alipay_public_key_path']).read(),
            sign_type=settings.ALIAPY_CONFIG['sign_type'],  # RSA 或者 RSA2
            debug=settings.ALIAPY_CONFIG['debug'],  # 默认False
        )
        # 校验支付宝响应数据
        data = request.query_params.dict()
        out_trade_no = data.get('out_trade_no')
        sign = data.pop('sign')
        success = alipay.verify(data,sign)
        print('status>>>',success)
        if not success:
            logger.error('%s,支付宝响应数据校验失败' % out_trade_no)
            return Response('支付宝响应数据校验失败',status=status.HTTP_400_BAD_REQUEST)

        res_data = self.change_order_status(data)

        #  响应结果
        return Response({'msg':'这一脚没毛病','data':res_data})



    def post(self,request):
        alipay = AliPay(
            appid=settings.ALIAPY_CONFIG['appid'],
            app_notify_url=None,  # 默认回调url
            app_private_key_string=open(settings.ALIAPY_CONFIG['app_private_key_path']).read(),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=open(settings.ALIAPY_CONFIG['alipay_public_key_path']).read(),
            sign_type=settings.ALIAPY_CONFIG['sign_type'],  # RSA 或者 RSA2
            debug=settings.ALIAPY_CONFIG['debug'],  # 默认False
        )
        # 校验支付宝响应数据
        data = request.data.dict()

        sign = data.pop('sign')
        success = alipay.verify(data,sign)
        if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED"):

            self.change_order_status(data)

            return Response('success')



    def change_order_status(self,data):
        with transaction.atomic():
            out_trade_no = data.get('out_trade_no')
            trade_no = data.get('trade_no')
            # 修改订单状态
            # try:
            order_obj = Order.objects.get(order_number=out_trade_no)
            order_obj.order_status = 1
            order_obj.save()
            # except Exception as e:
                # e 如何获取错误信息文本内容
                # return Response({'msg':'订单生成失败，没有找到该订单'},status=status.HTTP_400_BAD_REQUEST)

            # 修改优惠券的使用状态
            print('order_obj.coupon', order_obj.coupon)
            if order_obj.coupon > 0:
                user_coupon_obj = UserCoupon.objects.get(is_use=False, id=order_obj.coupon)
                user_coupon_obj.is_use = True
                user_coupon_obj.save()

            # 扣积分
            use_credit = order_obj.credit

            self.request.user.credit -= use_credit
            self.request.user.save()

            # 保存支付宝的交易流水号(购买记录表)

            order_detail_objs = order_obj.order_courses.all()
            now = datetime.datetime.now()

            conn = get_redis_connection('cart')
            pipe = conn.pipeline()
            pipe.delete('selected_cart_%s' % self.request.user.id)

            res_data = {
                'pay_time': now,
                'course_list': [],
                'total_real_price': order_obj.real_price,
            }

            for order_detail in order_detail_objs:
                course = order_detail.course
                course.students += 1
                course.save()
                res_data['course_list'].append(course.name)

                expire_id = order_detail.expire
                if expire_id > 0:
                    expire_obj = CourseExpire.objects.get(id=expire_id)

                    expire_time = expire_obj.expire_time
                    out_time = now + datetime.timedelta(days=expire_time)
                else:
                    out_time = None

                UserCourse.objects.create(**{
                    'user':self.request.user,
                    'course':course,
                    'trade_no':trade_no,
                    'buy_type':1,
                    'pay_time':now,
                    'out_time':out_time,

                })
                #　购物车ｒｅｄｉｓ数据删除

                pipe.hdel('cart_%s' % self.request.user.id, course.id)

            pipe.execute()

        return res_data
