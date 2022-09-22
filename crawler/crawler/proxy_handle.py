# -*- coding: utf-8 -*-


import json
import requests

import socket

def GetLocalIPByPrefix(prefix):
    """ 多网卡状况下，根据前缀获取IP（Windows 下适用） """
    localIP = ''
    print('本地ip地址：',socket.gethostbyname_ex(socket.gethostname()))
    for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
        if ip.startswith(prefix):
            localIP = ip
    
    return localIP
    
ip = GetLocalIPByPrefix('192.168')

def get_proxy():
    response = requests.get(f"http://{ip}:5010/get/").text
    result = json.loads(response)
    # print(result, type(result))
    return result['proxy']
 
def delete_proxy(proxy):
    requests.get("http://%s:5010/delete/?proxy={}" % (ip).format(proxy))
    