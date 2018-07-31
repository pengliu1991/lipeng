#!/usr/bin/env python
# coding:utf-8
#requests提交表单登陆

import requests,time
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import sys
from cookielib import LWPCookieJar

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
reload(sys)
sys.setdefaultencoding('utf8')

filename = 'cookie_ten'
session = requests.Session()
session.cookies = LWPCookieJar(filename)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "host": "www.hybrid-analysis.com",
    "Connection": "keep-alive",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.8",
}
def login():
    data = {
        "email": "528413269@qq.com",
        "password": "244466666",
    }
    try:
        resp = session.post('https://www.hybrid-analysis.com/login', data=data, headers=headers, verify=False)
        session.cookies.save(ignore_discard=True, ignore_expires=True)
        print "login scuess"
    except Exception as e:
        print "login error"
        print e
if __name__ == "__main__":
    try:
        session.cookies.load(filename= filename, ignore_discard=True)
        print "cookie加载成功"
        html = session.get("https://www.hybrid-analysis.com/search?filter=all&query=ppt&sort=^timestamp&page=1", headers=headers, allow_redirects=False, verify=False)
        print html.content
        #soup = BeautifulSoup(html, "lxml")

        #接着写你下面的
    except:
        print('Cookie未加载！')
        login()

