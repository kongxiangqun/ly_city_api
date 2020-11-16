from django.db import models

# Create your models here.

from luffyapi.settings import contains
from luffyapi.utils.models import BaseModel
from users.models import User
from course.models import Course,CourseExpire

class Order(BaseModel):
    """订单模型"""
    status_choices = (
        (0, '未支付'),
        (1, '已支付'),
        (2, '已取消'),
        (3, '超时取消'),
    )
    pay_choices = (
        (0, '支付宝'),
        (1, '微信支付'),
    )
    order_title = models.CharField(max_length=150,verbose_name="订单标题")
    total_price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="订单总价", default=0)
    real_price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="实付金额", default=0)
    order_number = models.CharField(max_length=64,verbose_name="订单号")
    order_status = models.SmallIntegerField(choices=status_choices, default=0, verbose_name="订单状态")
    pay_type = models.SmallIntegerField(choices=pay_choices, default=1, verbose_name="支付方式")
    credit = models.IntegerField(default=0, verbose_name="使用的积分数量")
    coupon = models.IntegerField(null=True, verbose_name="用户优惠券ID")
    order_desc = models.TextField(max_length=500, verbose_name="订单描述",null=True,blank=True)
    pay_time = models.DateTimeField(null=True, verbose_name="支付时间")
    user = models.ForeignKey(User, related_name='user_orders', on_delete=models.DO_NOTHING,verbose_name="下单用户")

    class Meta:
        db_table="ly_order"
        verbose_name= "订单记录"
        verbose_name_plural= "订单记录"

    def __str__(self):
        return "%s,总价: %s,实付: %s" % (self.order_title, self.total_price, self.real_price)

    def order_detail_data(self):
        order_detail_objs = self.order_courses.all()
        data_list = [

        ]

        for order_detail in order_detail_objs:
            expire_id = order_detail.expire
            if expire_id > 0:
                expire_obj = CourseExpire.objects.get(id=expire_id)
                expire_text = expire_obj.expire_text
            else:
                expire_text = '永久有效'

            order_dict = {
                'course_img': contains.SERVER_ADDR + order_detail.course.course_img.url,
                'course_name': order_detail.course.name,
                'expire_text': expire_text,
                'price': order_detail.price,
                'real_price': self.real_price,
                'discount_name': order_detail.discount_name,

            }
            data_list.append(order_dict)

        return data_list


# '''
# order_dict:[
#     {
#         订单id:'xxx',
#         订单号：'xxxx',
#         course_list:[
#             {
#                 'course_id':1,
#                 'course_name':'flask框架'
#             },
#             {
#                 'course_id':1,
#                 'course_name':'flask框架'
#             },
#         ]
#     },
#     {
#         订单id:'xxx',
#         订单号：'xxxx',
#         course_list:[
#             {
#                 'course_id':1,
#                 'course_name':'flask框架'
#             },
#             {
#                 'course_id':1,
#                 'course_name':'flask框架'
#             },
#         ]
#     }
#
#
# ]
#
# '''


class OrderDetail(BaseModel):
    """
    订单详情
    """
    order = models.ForeignKey(Order, related_name='order_courses', on_delete=models.CASCADE, verbose_name="订单ID")
    course = models.ForeignKey(Course, related_name='course_orders', on_delete=models.CASCADE, verbose_name="课程ID")
    expire = models.IntegerField(default='0', verbose_name="有效期周期",help_text="0表示永久有效")
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="课程原价")
    real_price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="课程实价")
    discount_name = models.CharField(max_length=120,default="",verbose_name="优惠类型")

    class Meta:
        db_table="ly_order_detail"
        verbose_name= "订单详情"
        verbose_name_plural= "订单详情"

    def __str__(self):
        return "%s" % (self.course.name)


