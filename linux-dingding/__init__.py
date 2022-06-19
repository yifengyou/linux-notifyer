#!/usr/bin/env python

import base64
import hashlib
import urllib
import time
import hmac
import requests
import json

DINGDING_SECRET = "SEC9d3c70d73a5954e9bcee9413f03ca3f4e24c5eaeb1462af7c2639919d9564bc8"
DINGDING_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=b015523c5706073a1fbed5bc8171d5012a7d36b90b587091a6dfe3453e5532f9"

def dingdingAlert(msg):
    timestamp = str(round(time.time() * 1000))
    secret = DINGDING_SECRET
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

    webhook = '{}&timestamp={}&sign={}'.format(DINGDING_WEBHOOK,timestamp, sign)
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "text",
        "text": {
            "content": msg,
        },
    }
    x = requests.post(url=webhook, data=json.dumps(data), headers=headers)
    if x.json()["errcode"] != 0:
        print("dingding false")

def main():
    dingdingAlert("linux-dingding")

if __name__ == "__main__":
    main()
