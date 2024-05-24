# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProxyHandler.py
   Description :
   Author :       JHao
   date：          2016/12/3
-------------------------------------------------
   Change Activity:
                   2016/12/03:
                   2020/05/26: 区分http和https
-------------------------------------------------
"""
__author__ = 'JHao'

from helper.proxy import Proxy
from db.dbClient import DbClient
from handler.configHandler import ConfigHandler
from datetime import datetime
import json
from util.webRequest import WebRequest


class ProxyHandler(object):
    """ Proxy CRUD operator"""

    def __init__(self):
        self.conf = ConfigHandler()
        self.db = DbClient(self.conf.dbConn)
        self.db.changeTable(self.conf.tableName)

    def get(self, https=False):
        """
        return a proxy
        Args:
            https: True/False
        Returns:
        """
        proxy = self.db.get(https)
        return Proxy.createFromJson(proxy) if proxy else None

    def pop(self, https):
        """
        return and delete a useful proxy
        :return:
        """
        proxy = self.db.pop(https)
        if proxy:
            return Proxy.createFromJson(proxy)
        return None

    def put(self, proxy):
        """
        put proxy into use proxy
        :return:
        """
        self.db.put(proxy)

    def delete(self, proxy):
        """
        delete useful proxy
        :param proxy:
        :return:
        """
        return self.db.delete(proxy.proxy)

    def getAll(self, https=False):
        """
        get all proxy from pool as Proxy list
        :return:
        """
        proxies = self.db.getAll(https)
        return [Proxy.createFromJson(_) for _ in proxies]

    def exists(self, proxy):
        """
        check proxy exists
        :param proxy:
        :return:
        """
        return self.db.exists(proxy.proxy)

    def getCount(self):
        """
        return raw_proxy and use_proxy count
        :return:
        """
        total_use_proxy = self.db.getCount()
        return {'count': total_use_proxy}

    def updateUseRecord(self, proxy):
        s = self.db.getUseRecord(proxy)
        if s:
            data = json.loads(s)
            data['use_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data['use_count'] = data['use_count'] + 1 if 'use_count' in data else 2
        else:
            data = {
                'proxy': proxy,
                'use_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'region': self.regionGetter(proxy.split(':')[0]),
                'use_count': 1,
            }
        return self.db.updateUseRecord(proxy, json.dumps(data, ensure_ascii=False))

    def getAllUseRecord(self):
        def sort_key(x):
            # return int(x['use_count']) if 'use_count' in x else 1
            return x['use_time']

        use_records = self.db.getAllUseRecord()
        list_json = [json.loads(x) for x in use_records]
        list_json = sorted(list_json, key=sort_key, reverse=True)
        return list_json

    def getValid(self):
        use_records = self.db.getAllUseRecord()
        # 保护期内的ip
        invalid_ip = []
        for record in use_records:
            record_json = json.loads(record)
            delta_time = datetime.now() - datetime.strptime(record_json['use_time'], "%Y-%m-%d %H:%M:%S")
            if delta_time.days < 1:
                invalid_ip.append(record_json['proxy'].split(':')[0])
            # else:
            #     print('delete proxy >> {}'.format(record_json))
            #     self.db.deleteUseRecord(record_json['proxy'])
        print('invalid_ip >> {}'.format(invalid_ip))

        # 去除保护期内的ip
        proxies = self.db.getAll(True)
        valid_proxies = []
        for proxy in proxies:
            proxy_json = json.loads(proxy)
            if proxy_json['proxy'].split(':')[0] not in invalid_ip:
                valid_proxies.append(proxy_json)
        valid_proxies = sorted(valid_proxies, key=lambda x: x['last_time'], reverse=True)
        return {
            'valid_proxies': valid_proxies,
            'invalid_ip_num': len(invalid_ip),
            'total_num': len(proxies)
        }

    def regionGetter(self, ip):
        try:
            url = 'https://searchplugin.csdn.net/api/v1/ip/get?ip=%s' % ip
            r = WebRequest().get(url=url, retry_time=1, timeout=2).json
            return r['data']['address']
        except:
            return 'error'
