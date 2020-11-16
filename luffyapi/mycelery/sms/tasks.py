from mycelery.main import app


from luffyapi.libs.ronglian_sms_sdk.sms import send_message
from django.conf import settings
from luffyapi.settings import contains

import logging
logger = logging.getLogger('django')

@app.task(name='smsCode')
def sms_codes(phone,sms_code):
    ret = send_message(settings.SMS_INFO.get('TID'), phone, (sms_code, contains.SMS_CODE_EXPIRE_TIME // 60))
    if not ret:
        logger.error('{}手机号短信发送失败'.format(phone))
    return '短信发送成功啦^-^'


@app.task
def sms_code2():
    print('xxxx')
    return '发送短信成功2'


