#!/usr/local/bin/python
#-*- coding:utf-8 -*-
# Author: jacky
# Time: 14-2-22 下午11:48
# Desc: 短信http接口的python代码调用示例
import httplib
import urllib
#服务地址
host = "yunpian.com"
#端口号
port = 80
#版本号
version = "v1"
#查账户信息的URI
user_get_uri = "/" + version + "/user/get.json"
#通用短信接口的URI
sms_send_uri = "/" + version + "/sms/send.json"
#模板短信接口的URI
sms_tpl_send_uri = "/" + version + "/sms/tpl_send.json"

def get_user_info(apikey):
    """
    取账户信息
    """
    conn = httplib.HTTPConnection(host, port=port)
    conn.request('GET', user_get_uri + "?apikey=" + apikey)
    response = conn.getresponse()
    response_str = response.read()
    conn.close()
    return response_str

def send_sms(apikey, text, mobile):
    """
    能用接口发短信
    """
    params = urllib.urlencode({'apikey': apikey, 'text': text, 'mobile':mobile})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection(host, port=port, timeout=30)
    conn.request("POST", sms_send_uri, params, headers)
    response = conn.getresponse()
    response_str = response.read()
    conn.close()
    return response_str

def tpl_send_sms(apikey, tpl_id, tpl_value, mobile):
    """
    模板接口发短信
    """
    params = urllib.urlencode({'apikey': apikey, 'tpl_id':tpl_id, 'tpl_value': tpl_value, 'mobile':mobile})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection(host, port=port, timeout=30)
    conn.request("POST", sms_tpl_send_uri, params, headers)
    response = conn.getresponse()
    response_str = response.read()
    conn.close()
    return response_str

def send_short_message(mobile=None,valicode=None):
    apikey = "6854b8e7d98b9701fb031ca528523138"
    if not mobile:
        return 0
    if not valicode:
        return 0

    text = "您的验证码是"+valicode+" 【逗脸】"
    #查账户信息
    # print(get_user_info(apikey))
    #调用通用接口发短信
    raw_response=send_sms(apikey, text, mobile)
    return 1
    # if 发送成功:
    #     return 1
    # else:
    #     return 0

if __name__ == '__main__':
    apikey = "6854b8e7d98b9701fb031ca528523138"
    #查账户信息
    print(get_user_info(apikey))
    #调用通用接口发短信
    text = "您的验证码是123456 【逗脸】"
    mobile="15629181795"
    print(send_sms(apikey, text, mobile))






                            