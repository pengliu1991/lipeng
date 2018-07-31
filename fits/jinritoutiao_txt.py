#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests

read_file = r"C:\Users\upeng\Desktop\bbb.txt"
write_file = read_file.split(".txt")[0] + "_txt.txt"
open_read_file = open(read_file)
open_write_file = open(write_file, 'w')
headers = {}
url = ""
for line in open_read_file.readlines():
    if ":" in line:
        key = line.split(":")[0].strip()
        value = line.split(":")[1].strip()
        headers[key] = value
    if "HTTP/1.1" in line:
        url = line.split(" ")[1].split("HTTP/1.1")[0].strip()
#print headers
#print url
get_content = requests.get(url=url, headers=headers)
open_write_file.write(get_content.content)
open_read_file.close()
open_write_file.close()