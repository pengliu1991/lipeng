#!/usr/bin/env python
# coding:utf-8
#requests提交表单登陆

#import urllib.request, urllib.parse, urllib.error
import urllib, urllib2
import http

LOGIN_URL = 'https://www.hybrid-analysis.com'
values = {'user': '528413269@qq.com', 'password': '244466666'}
postdata = urllib.parse.urlencode(values).encode()
user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
headers = {'User-Agent': user_agent, 'Connection': 'keep-alive'}

cookie_filename = 'cookie.txt'
cookie = http.cookiejar.MozillaCookieJar(cookie_filename)
handler = urllib.request.HTTPCookieProcessor(cookie)
opener = urllib.request.build_opener(handler)

request = urllib.request.Request(LOGIN_URL, postdata, headers)
response = opener.open(request)