# -*- coding: utf-8 -*-

import re
import os
import csv
import string
import requests
from urllib.parse import quote
from multiprocessing import Pool


BASE_URL = 'http://172.16.0.1/VirusSamples/'
BLOCK_INFO = "访问的URL中含有安全风险"
PROXIES = {'http': 'http://172.18.200.240:8080'}


def get_url(base_url):
    """
    爬取目标url中可下载文件（不包含文件夹内文件）
    :param base_url:
    :return: URL_list（Generator）
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/67.0.3396.99 Safari/537.36'
        }
        r = requests.get(base_url, headers=headers, proxies=PROXIES, verify=False)
        print(r.status_code)
        result = r.text
    except Exception as e:
        print(e)
    if result:
        # pattern = re.compile(r"alt=\"\[(?!DIR|ICO).*?<a href=.*?>(.*?)</a>", re.S)
        pattern = re.compile(r"<a href=.*?>(.*?)</a>", re.S)
        fn = re.findall(pattern, result)
        return [base_url + i for i in fn]

def get_url1(from_file='url16000.txt'):
    """
    从文件中获取目标url
    :param base_url:
    :return: URL_list（Generator）
    """
    txtfile = open(from_file, 'r')#'encoding='utf-8')
    url_list = txtfile.readlines()
    for i in range(0,len(url_list)):
        url_list[i] = url_list[i].replace('\n','')
        if "http://" not in url_list[i]:
            url_list[i] = "http://" + url_list[i]
    return url_list
    
    
def encodeURL(url):
    """
    处理包含中文字符串/空格的URL编码问题
    :param url:
    :return:
    """
    return quote(url, safe=string.printable).replace(' ', '%20')


def write2csv(data):
    try:
        with open('aswg_result.csv', 'a', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data)
    except Exception as e:
        print(e)


def main(url):
    """
    下载文件，分析是否被SWG阻断
    :param url:
    :return: callback
    """
    try:
        r = requests.get(encodeURL(url), proxies=PROXIES, verify=False)
        print(url, r.status_code)
        if r.status_code == 403:
            r.encoding = 'utf-8'
            if BLOCK_INFO in r.text:
                return [url, url.split('/')[-1], r.status_code, BLOCK_INFO]
            else:
                return [url, url.split('/')[-1], r.status_code, "other"]
        else:
            return [url, url.split('/')[-1], r.status_code, 'pass']
    except Exception as e:
        print(e)
        return [url, url.split('/')[-1], 0, e]


if __name__ == '__main__':
    if os.path.exists('result.csv'):
        os.remove('result.csv')
    print('文件总数： ', len(get_url1()))

    pool = Pool()
    for url in get_url1():
        pool.apply_async(main, (url,), callback=write2csv)
    pool.close()
    pool.join()

