# -*- coding: utf-8 -*-

import json
import datetime
from app.models import Report
from flask import Response


## 字符串转字典
def str_to_dict(dict_str):
    # logging.debug(dict_str)
    if isinstance(dict_str, str) and dict_str != '':
        new_dict = json.loads(dict_str)
    else:
        new_dict = ""
    # logging.debug(new_dict)
    return new_dict


# 字典转对象
def dict_to_obj(dict, obj, exclude=None):
    for key in dict:
        if exclude:
            if key in exclude:
                continue
        setattr(obj, key, dict[key])
    return obj


# peewee转dict
def obj_to_dict(obj, exclude=None):
    dict = obj.__dict__['_data']
    if exclude:
        for key in exclude:
            if key in dict: dict.pop(key)
    return dict


# peewee转list
def query_to_list(query, exclude=None):
    list = []
    for obj in query:
        dict = obj_to_dict(obj, exclude)
        list.append(dict)
    return list


# 封装HTTP响应
def jsonresp(jsonobj=None, status=200, errinfo=None):
    if status >= 200 and status < 300:
        jsonstr = json.dumps(jsonobj, ensure_ascii=False, default=datetime_handler)
        return Response(jsonstr, mimetype='application/json', status=status)
    else:
        return Response('{"errinfo":"%s"}' % (errinfo,), mimetype='application/json', status=status)


# JSON中时间格式处理
def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        # return x.isoformat()
        return x.strftime("%Y-%m-%d %H:%M:%S")
    raise TypeError("Unknown type")
    # json.dumps(data, default=datetime_handler)


# 通过名称获取PEEWEE模型
def get_model_by_name(model_name):
    if model_name == 'reports':
        DynamicModel = Report
    else:
        DynamicModel = None
    return DynamicModel
