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
import re
from helper import validator


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

    def updateUseRecord(self, proxy, time=None):
        s = self.db.getUseRecord(proxy)
        if s:
            data = json.loads(s)
            data['use_time'] = time if time else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data['use_count'] = data['use_count'] + 1 if 'use_count' in data else 2
        else:
            data = {
                'proxy': proxy,
                'use_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'region': self.regionGetter(proxy.split(':')[0]),
                'use_count': 1,
            }
        return self.db.updateUseRecord(proxy, json.dumps(data, ensure_ascii=False))

    def deleteUseRecord(self, proxy):
        return self.db.deleteUseRecord(proxy)

    def getAllUseRecord(self):
        def sort_key(x):
            # return int(x['use_count']) if 'use_count' in x else 1
            return x['use_time']

        use_records = self.db.getAllUseRecord()
        list_json = [json.loads(x) for x in use_records]
        list_json = sorted(list_json, key=sort_key, reverse=True)
        return list_json

    def getValid(self):
        use_records = [json.loads(x) for x in self.db.getAllUseRecord()]
        # 保护期内的ip
        invalid_ip = []
        for record in use_records:
            delta_time = datetime.now() - datetime.strptime(record['use_time'], "%Y-%m-%d %H:%M:%S")
            if delta_time.days < 1:
                invalid_ip.append(record['proxy'].split(':')[0])
            # else:
            #     print('delete proxy >> {}'.format(record_json))
            #     self.db.deleteUseRecord(record_json['proxy'])
        print('invalid_ip >> {}'.format(invalid_ip))

        # 去除保护期内的ip
        proxies = [json.loads(x) for x in self.db.getAll(True)]
        valid_proxies = []
        for proxy in proxies:
            if proxy['proxy'].split(':')[0] not in invalid_ip:
                valid_proxies.append(proxy)
        valid_proxies = sorted(valid_proxies, key=lambda x: x['last_time'], reverse=True)

        def get_use_record(use_records, ip):
            for use_record in use_records:
                if use_record['proxy'].split(':')[0] == ip:
                    return use_record

        results = []
        for valid_proxy in valid_proxies:
            use_record = get_use_record(use_records, valid_proxy['proxy'].split(':')[0])
            result = {}
            result['proxy'] = valid_proxy['proxy']
            result['region'] = valid_proxy['region']
            result['source'] = valid_proxy['source']
            result['last_time'] = valid_proxy['last_time']
            result['check_count'] = valid_proxy['check_count']
            result['use_count'] = \
                use_record['use_count'] if use_record and 'use_count' in use_record else 1 if use_record else 0
            result['use_time'] = use_record['use_time'] if use_record and 'use_time' in use_record else '-1'
            results.append(result)
        return {
            'valid_proxies': results,
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

    def batchUpdateUseRecord(self, data):
        print("batchUpdateUseRecord")
        s = data.decode('utf-8')
        # print("s >> {}".format(s))

        proxies = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+', s)
        default_time = '2024-01-01 00:00:00'
        for proxy in proxies:
            record = self.db.getUseRecord(proxy)
            if record:
                print("proxy {} 已存在...".format(proxy))
                continue

            print("插入 proxy: {}, time: {}".format(proxy, default_time))
            data = {
                'proxy': proxy,
                'use_time': default_time,
                'region': self.regionGetter(proxy.split(':')[0]),
                'use_count': 1,
            }
            self.db.updateUseRecord(proxy, json.dumps(data, ensure_ascii=False))
        return

    def fix_data(self):
        all_records = [json.loads(x) for x in self.db.getAllUseRecord()]
        default_time = '2024-01-01 00:00:00'
        for record in all_records:
            if record['use_time'] < "2024-05-26 14:00:00":
                print("valid proxy: {}, time: {}".format(record['proxy'], record['use_time']))
                continue
            print("fix proxy: {}, time: {}".format(record['proxy'], record['use_time']))
            self.updateUseRecord(record['proxy'], default_time)
        pass

    def updateUseRecordStatus(self):
        records = [json.loads(x) for x in self.db.getAllUseRecord()]
        for record in records:
            proxy = record['proxy']
            res = validator.httpsTimeOutValidator(proxy)
            print("proxy >> {}, res >> {}".format(proxy, res))
            pass
