from celery.result import AsyncResult
from mycelery.sms.tasks import sms_code2

ret = sms_code2.delay()
async_task = AsyncResult(id=ret.id,app=sms_code2)

print(async_task.successful())
result = async_task.get()
print(result)

