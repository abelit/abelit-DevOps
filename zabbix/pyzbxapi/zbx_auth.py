# -*- coding:utf-8 -*-
import json
import requests

url = 'http://58.42.231.98:50080/zabbix/api_jsonrpc.php'
post_headers = {'Content-Type': 'application/json'}
post_data = {
    "jsonrpc": "2.0",
    "method": "user.login",
    "params": {
        "user": "Admin",
        "password": "zabbix"
    },
    "id": 1
}

ret = requests.post(url, data=json.dumps(post_data), headers=post_headers)
print(ret.text)
