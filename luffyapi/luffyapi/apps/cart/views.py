from django.shortcuts import render
from rest_framework.viewsets import ViewSet
# Create your views here.
from django_redis import get_redis_connection
from course import models
from rest_framework.response import Response
from rest_framework import status
from luffyapi.settings import contains
from rest_framework.permissions import IsAuthenticated

import logging

logger = logging.getLogger('django')


class AddCartView(ViewSet):
    permission_classes = [IsAuthenticated, ]  # 请求头里面必须带着token
    def add(self, request):
        # print('>>>>>>>>>>>>>>>',request.user)

        course_id = request.data.get('course_id')
        user_id = 1

        # 存储有效期
        expire = 0  # 表示永久有效
        conn = get_redis_connection('cart')

        try:
            models.Course.objects.get(id=course_id)
        except:

            return Response({'msg': '课程不存在'}, status=status.HTTP_400_BAD_REQUEST)

        # set type
        '''
        user_id:{
            course_id:expire,
            course_id:expire,
        }

        '''

        pipe = conn.pipeline()  # 创建管道,
        pipe.multi()

        # 批量操作
        pipe.hset('cart_%s' % user_id, course_id, expire)
        # pipe.hset('cart_%s'%user_id, course_id , expire)
        # pipe.hset('cart_%s'%user_id, course_id , expire)
        # pipe.hset('cart_%s'%user_id, course_id , expire)

        pipe.execute()

        # conn.sadd('cart_%s'%user_id, course_id)
        # cart_length = conn.scard('cart_%s'%user_id)
        cart_length = conn.hlen('cart_%s' % user_id)
        print('cart_length', cart_length)

        return Response({'msg': '添加成功', 'cart_length': cart_length})

    def cart_list(self, request):
        # requset.user
        # user_id = 1
        user_id = request.user.id
        conn = get_redis_connection('cart')

        conn.delete('selected_cart_%s' % user_id)

        ret = conn.hgetall('cart_%s' % user_id)  # dict {b'1': b'0', b'2': b'0'}
        cart_data_list = []
        print(ret)
        try:
            # for cid, eid in ret.items():
            #     course_id = cid.decode('utf-8')
            #     expire_id = eid.decode('utf-8')
            #
            #     course_obj = models.Course.objects.get(id=course_id)
            #
            #     cart_data_list.append({
            #         'name': course_obj.name,
            #         'course_img': contains.SERVER_ADDR + course_obj.course_img.url,
            #         'price': course_obj.price,
            #         'expire_id': expire_id
            #     })
            for cid, eid in ret.items():
                course_id = cid.decode('utf-8')
                # expire_id = int(eid.decode('utf-8'))
                expire_id = 0
                course_obj = models.Course.objects.get(id=course_id)

                cart_data_list.append({
                    'course_id': course_obj.id,
                    'name': course_obj.name,
                    'course_img': contains.SERVER_ADDR + course_obj.course_img.url,
                    'price': course_obj.price,
                    'real_price': course_obj.real_price(),
                    'expire_id': expire_id,
                    'expire_list': course_obj.get_expire(),
                    'selected': False,  # 默认没有勾选
                })
        except Exception:
            logger.error('获取购物车数据失败')
            return Response({'msg': '后台数据库出问题了,请联系管理员'}, status=status.HTTP_507_INSUFFICIENT_STORAGE)
            # try:
        #     models.Course.objects.filter()
        print(cart_data_list)

        return Response({'msg': 'xxx', 'cart_data_list': cart_data_list})

    # 勾选
    def change_select(self, request):
        # 拿到课程id
        course_id = request.data.get('course_id')

        try:
            models.Course.objects.get(id=course_id)
        except:
            return Response({'msg': '课程不存在，不要乱搞！'}, status=status.HTTP_400_BAD_REQUEST)
        # 拿到用户id
        user_id = request.user.id
        conn = get_redis_connection('cart')  # 1:{1,3}
        # 存数据 用户id 课程id 通过课程id找到真实价格 集合来存就可以
        # 1:{1,2,3} 1用户勾选的1 2 3 课程 删除3 1:{1,2}
        conn.sadd('selected_cart_%s' % user_id, course_id)

        return Response({'msg': '恭喜你！勾选成功！'})
    # 取消勾选
    def cancel_select(self, request):
        course_id = request.data.get('course_id')

        try:
            models.Course.objects.get(id=course_id)
        except:
            return Response({'msg': '课程不存在，不要乱搞！'}, status=status.HTTP_400_BAD_REQUEST)

        user_id = request.user.id
        conn = get_redis_connection('cart')  # 1:{1,3}
        conn.srem('selected_cart_%s' % user_id, course_id)

        return Response({'msg': '恭喜你！少花钱了，但是你真的不学习了吗！'})

    # 切换有效期,去redis中修改数据
    def change_expire(self,request):
        # 要修改有效期就要知道对应的用户id及课程id
        user_id = request.user.id
        course_id = request.data.get('course_id')
        # 修改后的有效期
        expire_id = request.data.get('expire_id')
        # 在add里面查过拿过来就行 课程存不存在
        try:
            course_obj = models.Course.objects.get(id=course_id)
        except:

            return Response({'msg':'课程不存在'},status=status.HTTP_400_BAD_REQUEST)
        # 看课程有效期 永久有效排除在外
        try:
            if expire_id > 0:
             expire_object = models.CourseExpire.objects.get(id=expire_id)
        except:

            return Response({'msg':'课程有效期不存在'},status=status.HTTP_400_BAD_REQUEST)

        # 有效期表中存着不同有效期对应的不同价格
        real_price = course_obj.real_price(expire_id)

        # 链接redis数据库
        conn = get_redis_connection('cart')
        # 修改那个用户下的哪个课程的有效期是多少
        conn.hset('cart_%s' % user_id, course_id, expire_id)

        return Response({'msg':'切换成功！', 'real_price': real_price})


    # 删除购物车数据
    def delete_course(self,request):
        user_id = request.user.id
        course_id = request.query_params.get('course_id')
        print('course_id>>>',course_id)
        conn = get_redis_connection('cart')
        pipe = conn.pipeline()

        pipe.hdel('cart_%s' % user_id, course_id)
        pipe.srem('selected_cart_%s' % user_id, course_id)

        pipe.execute()

        return Response({'msg':'删除成功'})

    # 结算页面数据
    def show_pay_info(self,request):
        user_id = request.user.id
        conn = get_redis_connection('cart')
        select_list = conn.smembers('selected_cart_%s' % user_id)
        data = []

        ret = conn.hgetall('cart_%s' % user_id)  # dict {b'1': b'0', b'2': b'0'}

        # print(ret)
        # 原价总价钱
        total_price = 0
        # 真实价格
        total_real_price = 0
        for cid, eid in ret.items():
            expire_id = int(eid.decode('utf-8'))
            if cid in select_list:

                course_id = int(cid.decode('utf-8'))
                course_obj = models.Course.objects.get(id=course_id)

                if expire_id > 0:
                    expire_obj = models.CourseExpire.objects.get(id=expire_id)
                    course_real_price = course_obj.real_price(expire_id)
                    # 总的真实价格
                    total_real_price += course_real_price
                    data.append({
                        'course_id':course_obj.id,
                        'name':course_obj.name,
                        'course_img':contains.SERVER_ADDR + course_obj.course_img.url ,
                        'real_price':course_real_price,
                        'expire_text':expire_obj.expire_text,
                    })
                else:
                    course_real_price = course_obj.real_price(expire_id)
                    total_real_price += course_real_price
                    data.append({
                        'course_id': course_obj.id,
                        'name': course_obj.name,
                        'course_img': contains.SERVER_ADDR + course_obj.course_img.url,
                        'real_price': course_real_price,
                        'expire_text': '永久有效',
                    })


        return Response({'data':data,'total_real_price':total_real_price})








