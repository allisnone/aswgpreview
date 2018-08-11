# -*- coding: utf-8 -*-
import json
import re
import os
import csv
import string
import requests
from urllib.parse import quote
import config

class URLrequest:
    def __init__(self,url,proxy=None,type='get',verify=False,initialize=True):
        self.url = url
        self.proxy = proxy
        self.type = type
        self.verify = verify
        self.status_code = -2
        if initialize:
            self.get_http_repsonse()
    
    def _encodeURL(self):
        """
        处理包含中文字符串/空格的URL编码问题
        :param url:
        :return:
        """
        return quote(self.url, safe=string.printable).replace(' ', '%20')
    
    def update_url(self,url):
        self.url = url
    
    def set_proxy(self,proxy):
        self.proxy = proxy
        
    def set_type(self,type):
        self.type = type

    def get_http_repsonse(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/67.0.3396.99 Safari/537.36'
        }
        r = requests.get(self._encodeURL(), proxies=self.proxy, verify=self.verify)
        #print(self.url, r.status_code)
        if self.type == 'post':
            s = json.dumps({'key1': 'value1', 'key2': 'value2'})
            r = requests.post(self.url, data=s)
        self.status_code = r.status_code
        #print(r.text)
        return r
    
    def post_http_repsonse(self):
        #sogaoqing
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/67.0.3396.99 Safari/537.36'
        }
        #r = requests.get(self._encodeURL(), proxies=self.proxy, verify=self.verify)
        #print(self.url, r.status_code)
        #if self.type == 'post':
        #s = json.dumps({'content': '13688845789'})
        s = json.dumps({'content': '450104198311190536'})
        #s = json.dumps({'file': '@securypreview_credit_card.txt'})
        r = requests.post(self.url, data=s,proxies=self.proxy, verify=self.verify)
        self.status_code = r.status_code
        #print(r.text)
        return r
    
    def is_aswg_block(self,urls,match_code=403,threshold=0.99):
        """
        所有URL使用相同的proxy，返回成功率
        """
        if not urls:
            return -1
        count_200_ok = 0
        count_403 = 0
        for url in urls:
            self.update_url(url)
            r = self.get_http_repsonse()
            
            if r.status_code == 200:
                count_200_ok = count_200_ok + 1
            elif r.status_code == 403:
                count_403 = count_403 + 1
            else:
                print(url)
                print('r.status_code=',r.status_code)
        if (count_200_ok + count_403) < len(urls)*0.5:
            #print('Please update urls, two many dead URL')
            #self.update_test_urls()
            return -2
        #print('200 ok: ', count_200_ok)
        #print('403 block: ', count_403)
        return int(count_403>=len(urls)*threshold)

class Securitypreview():
    def __init__(self,aswg_proxy=None,conf={}):
        self.aswg_proxy = aswg_proxy
        self.security_config = conf
        pass
    
    def set_aswg_proxy(self,aswg_proxy):
        self.aswg = aswg_proxy
        return
    
    def reset_security_config(self):
        self.security_config = config.SECURITY_CONFIG
        
    def set_security_config(self,conf={}):
        if conf:
            self.security_config = conf
    
    def get_security_config(self,mysql,username,passwd):
        return
    
    def get_security_result(self):
        result = self.security_config
        if not self.security_config:
            return {}
        for L1 in self.security_config.keys():
            if self.security_config[L1]:
                for L2 in self.security_config[L1].keys():
                    if self.security_config[L1][L2]:
                        for L3 in self.security_config[L1][L2].keys():
                            #print(L3)
                            urls = self.security_config[L1][L2][L3]['TEST URL']
                            #print('urls=',urls)
                            test_item = self.security_config[L1][L2][L3]
                            test_item['status'] = 'Failed'
                            aswg_block_status = -1
                            if urls:
                                http_mothod = test_item['mothod']
                                req = URLrequest(urls[0],proxy=self.aswg_proxy,type=http_mothod,initialize=False)
                                aswg_block_status = req.is_aswg_block(urls, match_code=403)
                                print('aswg_block_status=',aswg_block_status)
                                if req.is_aswg_block(urls, match_code=403)==1:
                                    test_item['status'] = 'success'
                            #"""
                            #print(result[L1][L2][L3]['TEST NAME'])
                            #print(result[L1][L2][L3])
                            if 'TEST DETAIL' in test_item.keys():
                                test_item.pop('TEST DETAIL')
                            if 'TEST DESCRIPTION' in test_item.keys():
                                test_item.pop('TEST DESCRIPTION')
                            #result.update({test_item['TEST NAME']:test_item})
                            #print(result)
                            #"""
                            urls = list()
        return result
    
    def get_result_without_aswg(self):
        return
    
    def get_result_protected_by_aswg(self):
        return
    
    def result_summary(self):
        return
    
"""    
url = 'http://www.sogaoqing.com/upload/url16000.txt'    
req = URLrequest(url)
print(req.status_code)
urls = [url]
print(req.is_aswg_block(urls, match_code=403))
"""
aswg_proxy = None
sp = Securitypreview()
sp.reset_security_config()
sp.set_aswg_proxy(aswg_proxy)

result1 = sp.get_security_result()
print(result1)
print('--------set proxy-----------')
#aswg_proxy = '172.18.200.240:8080'
aswg_proxy = {'http': 'http://172.18.200.240:8080'}
sp2 = Securitypreview(aswg_proxy)
#aswg_proxy = '49.4.84.41:8066'
#0aswg_proxy = '172.18.200.240:8080'
sp2.reset_security_config()
print(sp2.security_config)
sp2.set_aswg_proxy(aswg_proxy)
result2 = sp2.get_security_result()
print(result2)