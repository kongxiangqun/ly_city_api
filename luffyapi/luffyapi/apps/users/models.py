from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
from luffyapi.utils.models import BaseModel

class User(AbstractUser):
    phone = models.CharField(max_length=16,null=True,blank=True)
    wechat = models.CharField(max_length=16,null=True,blank=True)
    credit = models.IntegerField(default=0, blank=True, verbose_name="贝里")

    class Meta:
        db_table = 'ly_user'
        # 指定admin和xadmin中文显示名称
        verbose_name = '用户名'
        # 默认以复数显示表明 '用户名s',复数显示的时候也让它是 '用户名'
        verbose_name_plural = verbose_name

class Credit(BaseModel):
    """积分流水"""
    OPERA_OPION = (
        (1, "赚取"),
        (2, "消费"),
    )
    user = models.ForeignKey("User", related_name="user_credit", on_delete=models.CASCADE, verbose_name="用户")
    opera = models.SmallIntegerField(choices=OPERA_OPION, verbose_name="操作类型")
    number = models.SmallIntegerField(default=0, verbose_name="积分数值")

    class Meta:
        db_table = 'ly_credit'
        verbose_name = '积分流水'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s %s %s 贝壳" % (self.user.username, self.OPERA_OPION[self.opera][1], self.number)


from course.models import Course
class UserCourse(BaseModel):
    """用户的课程购买记录"""
    pay_choices = (
        (1, '用户购买'),
        (2, '免费活动'),
        (3, '活动赠品'),
        (4, '系统赠送'),
    )
    # 1   1
    # 1   2
    # 1   3
    # 2   1
    # 2   2

    user = models.ForeignKey(User, related_name='user_courses', on_delete=models.DO_NOTHING, verbose_name="用户")
    course = models.ForeignKey(Course, related_name='course_users', on_delete=models.DO_NOTHING, verbose_name="课程")
    trade_no = models.CharField(max_length=128, null=True, blank=True, verbose_name="支付平台的流水号", help_text="将来依靠流水号到支付平台查账单")
    buy_type = models.SmallIntegerField(choices=pay_choices, default=1, verbose_name="购买方式")
    pay_time = models.DateTimeField(null=True, blank=True, verbose_name="购买时间")
    out_time = models.DateTimeField(null=True, blank=True, verbose_name="过期时间") #null表示永不过期

    class Meta:
        db_table = 'ly_user_course'
        verbose_name = '课程购买记录'
        verbose_name_plural = verbose_name