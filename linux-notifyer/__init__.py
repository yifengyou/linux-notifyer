#!/usr/bin/env python3

import base64
import datetime
import hashlib
import subprocess
import urllib
import time
import hmac
import requests
import json
import configparser
import os

DEFULT_CONFIGFILE = "/etc/linux-notifyer/config"
DINGDING_SECRET = "SEC9d3c70d73a5954e9bcee9413f03ca3f4e24c5eaeb1462af7c2639919d9564bc8"
DINGDING_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=b015523c5706073a1fbed5bc8171d5012a7d36b90b587091a6dfe3453e5532f9"
GIT_REPOSITORY = "git@github.com:torvalds/linux.git"
GIT_BRANCH = "master"
GIT_DIRECTORY = "/home/linux.git/"
RETRY_TIMES = 3
WATCH = ['./']
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def dingdingAlert(msg):
    timestamp = str(round(time.time() * 1000))
    secret = DINGDING_SECRET
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

    webhook = '{}&timestamp={}&sign={}'.format(DINGDING_WEBHOOK, timestamp, sign)
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


def LoadConfig():
    global DINGDING_SECRET, DINGDING_WEBHOOK, RETRY_TIMES, GIT_REPOSITORY, WATCH, GIT_BRANCH, GIT_DIRECTORY

    config = configparser.ConfigParser(allow_no_value=True)
    if not os.path.exists(DEFULT_CONFIGFILE):
        print("can't find config file")
        exit(1)
    config.read(DEFULT_CONFIGFILE)
    if 'dingding_secret' in config['DEFAULT']:
        DINGDING_SECRET = config['DEFAULT']['dingding_secret']
    if 'dingding_webhook' in config['DEFAULT']:
        DINGDING_WEBHOOK = config['DEFAULT']['dingding_webhook']
    if 'retry_times' in config['DEFAULT']:
        RETRY_TIMES = config['DEFAULT']['retry_times']
    if 'git_repository' in config['DEFAULT']:
        GIT_REPOSITORY = config['DEFAULT']['git_repository']
    if 'git_branch' in config['DEFAULT']:
        GIT_BRANCH = config['DEFAULT']['git_branch']
    GIT_BRANCH = 'master' if '' == GIT_BRANCH else GIT_BRANCH
    if 'git_directory' in config['DEFAULT']:
        GIT_DIRECTORY = config['DEFAULT']['git_directory']
    if not os.path.exists(GIT_DIRECTORY):
        print("dir %s does't exists!" % GIT_DIRECTORY)
        exit(1)
    if 'watch' in config['DEFAULT']:
        WATCH = config['DEFAULT']['watch'].split()


def shell(cmd):
    # 执行cmd命令，如果成功，返回(0, 'xxx')；如果失败，返回(1, 'xxx')
    res = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)  # 使用管道
    result = res.stdout.read()  # 获取输出结果
    result += res.stderr.read()
    res.wait()  # 等待命令执行完成
    res.stdout.close()  # 关闭标准输出
    return result.decode("utf-8")


def UpdateGitRepo():
    update_msg = "Update repository:" + "\n"
    cmd = "git -C %s fetch --all" % (GIT_DIRECTORY)
    print(cmd)
    update_msg += shell(cmd) + "\n"
    return update_msg


def GetGitLog():
    # git log master --after='2022-06-27 01:00:00'
    git_msg = ""
    yesterday_timestamp = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
    for dir in WATCH:
        # print(dir)
        git_msg += " [%s] \n" % dir
        cmd = "git -C %s log --oneline master --after='%s' %s " % (GIT_DIRECTORY, yesterday_timestamp, str(dir))
        print(cmd)
        shell_output = shell(cmd)
        format_output = ""
        for line in shell_output.split('\n'):
            format_output += line.replace(' ', ':\n[忙疯了]', 1) + '\n\n'
            print(format_output)
        git_msg += format_output + "\n"
    return git_msg


def main():
    msg = "Message from linux-notifier" + "\n"
    msg += TIMESTAMP + "\n"
    msg += GIT_REPOSITORY + "\n"

    # load config
    LoadConfig()
    msg += "------------------------------\n"
    msg += UpdateGitRepo()
    msg += "------------------------------\n"
    # get git log info
    msg += GetGitLog()
    msg += "------------------------------\n"
    dingdingAlert(msg)
    print(TIMESTAMP)


if __name__ == "__main__":
    main()
