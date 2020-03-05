# -*- coding:utf-8 -*-
import json
import requests

url = 'http://58.42.231.98:50080/zabbix/api_jsonrpc.php'
post_headers = {'Content-Type': 'application/json'}
post_data = {
    "jsonrpc": "2.0",
    "method": "history.get",
    "params": {
        "output": "extend",
        "history": 0,
        "itemids": "23296",
        "sortfield": "clock",
        "sortorder": "DESC",
        "limit": 10
    },
    "id": 1,
    "auth": "6495cd076b5289e3f461f8e433838db8"  # 这是第一步获取的身份验证令牌
}

ret = requests.post(url, data=json.dumps(post_data), headers=post_headers)
print(ret.text)
