from .SmsSDK import SmsSDK
from django.conf import settings
accId = settings.SMS_INFO.get('ACCID')
accToken = settings.SMS_INFO.get('ACCTOKEN')
appId = settings.SMS_INFO.get('APPID')
import json


# accId = '8a216da8754a45d5017564dc514207fe'
# accToken = '759a69dae5134080b26cd1869069e410'
# appId = '8a216da8754a45d5017564dc52250804'

def send_message(tid, mobile, datas):
    sdk = SmsSDK(accId, accToken, appId)
    """
    tid = '1'
    mobile = '17833333641'
    datas = ('1234', '3')
    """
    resp = sdk.sendMessage(tid, mobile, datas)
    resp = json.loads(resp)
    print(resp) # {"statusCode":"000000","templateSMS":{"smsMessageSid":"ab994023e69f494b9dd8ceca9fa7fb4f","dateCreated":"20201102175602"}}
    return resp.get('statusCode') == '000000'


# send_message()
