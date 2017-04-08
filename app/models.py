# -*- coding: utf-8 -*-

from peewee import MySQLDatabase, Model, CharField, BooleanField, IntegerField, TextField, DateTimeField, fn
import datetime
import json
from werkzeug.security import check_password_hash
from flask_login import UserMixin
from conf.config import config
import os

cfg = config[os.getenv('FLASK_CONFIG') or 'default']

db = MySQLDatabase(host=cfg.DB_HOST, user=cfg.DB_USER, passwd=cfg.DB_PASSWD, database=cfg.DB_DATABASE)


class BaseModel(Model):
    class Meta:
        database = db

    def __str__(self):
        r = {}
        for k in self._data.keys():
            try:
                r[k] = str(getattr(self, k))
            except:
                r[k] = json.dumps(getattr(self, k))
        # return str(r)
        return json.dumps(r, ensure_ascii=False)


# 报表
class Report(BaseModel):
    batch_id = CharField()  # 测试批次
    check_date = DateTimeField(default=datetime.datetime.now)  # 测试时间
    sys_type = CharField()  # 系统类型
    domain_id = CharField()  # BSS域
    eparchy_name = CharField()  # 地市名
    staff_id = CharField()  # 测试工号
    serial_number = CharField()  # 测试号码
    check_desc = CharField()  # 测试内容
    check_flag = BooleanField()  # 测试成功标志：1成功0失败
    check_info = CharField(null=True)  # 测试结果
    check_response = TextField()  # HTTP响应
    resp_elapsed = CharField()  # HTTP响应时长


# 管理员工号
class User(UserMixin, BaseModel):
    username = CharField()  # 用户名
    password = CharField()  # 密码
    fullname = CharField()  # 真实性名
    email = CharField()  # 邮箱
    phone = CharField()  # 电话
    status = BooleanField(default=True)  # 生效失效标识

    def verify_password(self, raw_password):
        return check_password_hash(self.password, raw_password)


# 建表
def create_table():
    db.connect()
    db.create_tables([ Report, User])


if __name__ == '__main__':
    create_table()
