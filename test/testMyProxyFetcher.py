# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testProxyFetcher
   Description :
   Author :        JHao
   date：          2020/6/23
-------------------------------------------------
   Change Activity:
                   2020/6/23:
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.proxyFetcher import ProxyFetcher
from handler.configHandler import ConfigHandler
from lxml import html, etree
import os
import requests
import time
import random
import re
import sys
from requests.structures import CaseInsensitiveDict
import chardet
import json

import gzip
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_ip(tr):
    ips = tr.xpath('./td/abbr/text()')
    for ip in ips:
        if ip.strip():
            return ip.strip()
    ips = tr.xpath('./td/text()')
    for ip in ips:
        if ip.strip():
            return ip.strip()
    return None


def get_port(tr):
    ports = tr.xpath('./td/a/text()')
    for port in ports:
        if port.strip() and port.strip().isdigit():
            return port.strip()
    ports = tr.xpath('./td/text()')
    for port in ports:
        if port.strip() and port.strip().isdigit():
            return port.strip()
    return None


def get_request(url, proxies=None, headers=None):
    resp = requests.get(url, proxies=proxies, headers=headers, timeout=30)
    print(resp.status_code)
    return resp.content


def get_request_by_chrome(url, proxies=None):
    path = 'C:\Program Files\Chrome\Application\chromedriver.exe'
    chrome_optx = Options()  # 创建参数设置对象.
    chrome_optx.add_argument('--headless')  # 无界面化.
    chrome_optx.add_argument('--disable-gpu')  # 配合上面的无界面化.
    chrome_optx.add_argument('--window-size=1366,768')  # 设置窗口大小, 窗口大小会有影响
    chrome_optx.add_argument('--proxy-server=http://127.0.0.1:10809')
    chrome_optx.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36')
    driver = webdriver.Chrome(path, options=chrome_optx)
    driver.get(url)
    return driver.page_source


def write_page(page: bytes, name):
    with open('page/{}.html'.format(name), "w", encoding='utf-8') as f:
        f.write(page.decode('utf-8'))


def write_page_str(page: str, name):
    with open('page/{}.html'.format(name), "w", encoding='utf-8') as f:
        f.write(page)


def test():
    proxies = {
        "http": "http://127.0.0.1:10809",
        "https": "http://127.0.0.1:10809",
    }

    url = 'https://free-proxy-list.net/'
    page = get_request(url, proxies=proxies)
    print(page)

    x = etree.HTML(page)
    proxy_list = x.xpath('//table[@class="table table-striped table-bordered"]/tbody/tr')
    for tr in proxy_list:
        tds = tr.xpath('./td/text()')
        if tds:
            print('{}:{}'.format(tds[0], tds[1]))
        # yield ':'.join(tr.xpath('./td/text()')[0:2])
    return


def test2():
    proxies = {
        # "http": "http://127.0.0.1:10809",
        # "https": "http://127.0.0.1:10809",
    }
    url = 'https://www.freeproxy.world/?type=http&anonymity=&country=&speed=&port=&page=1'
    page = get_request(url, proxies=proxies)
    print(page)
    write_page(page, 'test2')
    # /html/body/div[3]/div[2]/table/tbody/tr[2]/td[1]
    x = etree.HTML(page)
    proxy_list = x.xpath('//table[@class="layui-table"]/tbody/tr')
    for tr in proxy_list:

        tds = tr.xpath('./td/text()')
        tas = tr.xpath('./td/a/text()')
        if tds and tas:
            print('{}:{}'.format(tds[0].strip(), tas[0]))

        # yield ':'.join(tr.xpath('./td/text()')[0:2])
    return


def test3():
    # https://github.com/vakhov/fresh-proxy-list/raw/master/http.txt
    proxies = {
        "http": "http://127.0.0.1:10809",
        "https": "http://127.0.0.1:10809",
    }
    url = 'https://github.com/vakhov/fresh-proxy-list/raw/master/http.txt'
    page = get_request(url, proxies=proxies)
    # print(page)
    write_page(page, 'test3')
    content = page.decode('utf-8')
    # print(content)
    for proxy in content.split('\r'):
        proxy = proxy.strip()
        if proxy:
            print(proxy)
            # yield proxy


def test4():
    # https://github.com/vakhov/fresh-proxy-list/raw/master/http.txt
    proxies = {
        "http": "http://127.0.0.1:10809",
        "https": "http://127.0.0.1:10809",
    }
    url = 'https://www.proxynova.com/proxy-server-list/country-us/'
    page = get_request(url, proxies=proxies)
    # print(page)
    write_page(page, 'test4')
    content = page.decode('utf-8')
    # print(content)
    # for proxy in content.split('\r'):
    #     proxy = proxy.strip()
    #     if proxy:
    #         print(proxy)
    # yield proxy


def test5():
    url = 'https://www.proxynova.com/proxy-server-list/country-us/'
    page = get_request_by_chrome(url)
    # print(page)
    write_page_str(page, 'test5')
    x = etree.HTML(page)
    proxy_list = x.xpath('//table[@class="table"]/tbody/tr')
    for tr in proxy_list:
        # /html/body/div[4]/div/table/tbody/tr[3]/td[1]/abbr/text()
        # /html/body/div[4]/div/table/tbody/tr[3]/td[2]/text()
        # /html/body/div[4]/div/table/tbody/tr[3]/td[2]/text()
        ip = get_ip(tr)
        port = get_port(tr)
        proxy = '{}:{}'.format(ip, port)
        print(proxy)


def test6():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        # 'Cookie': '__51vcke__20L1wEeeGTFXijbh=01a3a953-3017-50b3-abbc-633e7d6295f1; __51vuft__20L1wEeeGTFXijbh=1712924711508; __root_domain_v=.zdaye.com; _qddaz=QD.686512924711625; acw_tc=1a0c384b17196796663351486e005e654a6e775be4c75f73c247c6834340db; __51uvsct__20L1wEeeGTFXijbh=2; Hm_lvt_dd5f60791e15b399bf200ae217689c2f=1719679665; _qdda=3-1.1; _qddab=3-9mvpkr.ly0cve5x; ASPSESSIONIDSGCCCCSC=PBMEACBABGOHOIOLDOBPNKMF; __vtins__20L1wEeeGTFXijbh=%7B%22sid%22%3A%20%22c6be58a0-2cd5-520b-9427-676a6759957e%22%2C%20%22vd%22%3A%2017%2C%20%22stt%22%3A%2081238%2C%20%22dr%22%3A%2028290%2C%20%22expires%22%3A%201719681546515%2C%20%22ct%22%3A%201719679746515%7D; Hm_lpvt_dd5f60791e15b399bf200ae217689c2f=1719679747',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    url_temp = 'https://www.zdaye.com/free/{}'
    for pageNum in range(1, 2):
        url = url_temp.format(pageNum)
        print(url)
        page = get_request(url, headers=headers)
        print(page)
        # write_page_str(page.decode('utf-8'), 'test6')
        write_page_str(page.decode('gbk'), 'test6')
        # /html/body/div[3]/div[2]/table/tbody/tr[2]/td[1]
        x = etree.HTML(page)
        proxy_list = x.xpath('//table[@id="ipc"]/tbody/tr')
        for tr in proxy_list:
            tds = tr.xpath('./td/text()')
            print('{}:{}'.format(tds[0].strip(), tds[1].strip()))
    return

def test7():
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        # 'cookie': '__51vcke__K3h4gFH3WOf3aJqX=b8be1874-2474-5973-bd52-9d2b20199e70; __51vuft__K3h4gFH3WOf3aJqX=1684454647961; _gac_UA-76097251-1=1.1712925072.CjwKCAjwt-OwBhBnEiwAgwzrUhxaoXS3XVNg3gIaUzv-zI6Rnmg5bymglJAc9ivP9oXCrENMGBwXnxoCm30QAvD_BwE; _gcl_aw=GCL.1712925072.CjwKCAjwt-OwBhBnEiwAgwzrUhxaoXS3XVNg3gIaUzv-zI6Rnmg5bymglJAc9ivP9oXCrENMGBwXnxoCm30QAvD_BwE; _gcl_au=1.1.1762678950.1712925072; _ss_s_uid=303564d5ed632861cba244108f8fb59e; channelid=0; sid=1719741929841516; __51uvsct__K3h4gFH3WOf3aJqX=3; _gid=GA1.2.8699928.1719741931; __vtins__K3h4gFH3WOf3aJqX=%7B%22sid%22%3A%20%2269661d76-b7da-5393-bfdd-f736913469aa%22%2C%20%22vd%22%3A%207%2C%20%22stt%22%3A%20114202%2C%20%22dr%22%3A%203373%2C%20%22expires%22%3A%201719743844973%2C%20%22ct%22%3A%201719742044973%7D; _ga_DC1XM0P4JL=GS1.1.1719741930.4.1.1719742045.34.0.0; _ga=GA1.1.1732449351.1684454648',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }

    url_temp = 'https://www.kuaidaili.com/free/fps/{}'
    for pageNum in range(1, 4):
        url = url_temp.format(pageNum)
        print(url)
        page = get_request(url, headers=headers).decode('utf-8')
        # print(page)
        write_page_str(page, 'test7')

        str = re.findall(r'const fpsList = (\[.*]);', page)[0]
        print(str)
        data = json.loads(str)
        for item in data:
            proxy ='{}:{}'.format(item['ip'].strip(), item['port'].strip())
            print(proxy)
        time.sleep(2)
    return

if __name__ == '__main__':
    test7()
