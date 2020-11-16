# 任务队列的链接地址(变量名必须叫这个)
broker_url = 'redis://127.0.0.1:6379/14'
# 结果队列的链接地址(变量名必须叫这个)
result_backend = 'redis://127.0.0.1:6379/15'


from celery.schedules import crontab
from .main import app
# 定时任务的调度列表，用于注册定时任务
app.conf.beat_schedule = {
    # 每分钟查看订单状态
    'check_order_outtime': {
        # 本次调度的任务
        'task': 'cancle_order', # 这里的任务名称必须先到main.py中注册
        # 定时任务的调度周期
        # 'schedule': crontab(minute=0, hour=0),   # 每周凌晨00:00
        'schedule': crontab(),   # 每分钟
      	# 'args': (16, 16),  # 注意：任务就是一个函数，所以如果有参数则需要传递
    },
}



