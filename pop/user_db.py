#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Author  : mofei
# @Time    : 2018/10/11 22:41
# @File    : user_db.py
# @Software: PyCharm
import hashlib
import time
from django.db import connection


def get_by_ids(ids):
    ids = [str(id) for id in ids]
    cursor = connection.cursor()
    cursor.execute('select id,user_group_id,username,real_name,add_time,mobile ' +
                   'from user where id in (' + ','.join(ids) + ')')
    user_list = cursor.fetchall()
    cursor.close()
    result_user_list = []
    for user in user_list:
        user_dict = {'id': user[0], 'user_group_id': user[1],
                     'username': user[2], 'real_name': user[3],
                     'add_time': user[4], 'mobile': user[5]}
        result_user_list.append(user_dict)
    return result_user_list


def get_by_tel(tel):
    cursor = connection.cursor()
    cursor.execute('select id,user_group_id,username,real_name,add_time,mobile ' +
                   'from user where mobile = ' + tel)
    user = cursor.fetchone()
    cursor.close()
    return user


def add_user(tel, password=''):
    timestamp = int(time.time())
    # password = hashlib.md5((tel+str(timestamp)+password).encode('utf8')).hexdigest()
    cursor = connection.cursor()
    cursor.execute("insert into user(user_group_id,username,password,nickname,real_name," +
                   "qq_number,wangwang_number,weixin,email,add_time," +
                   "display,total,experience,score,login_time,ip,ip_address,mobile," +
                   "phone,zip,address,sex,path,presenter_id,presenter_username," +
                   "par_presenter_id,par_presenter_username,remark_time,remark," +
                   "pop_code,admin_id,admin_add_time,qq_unionid,wx_unionid,wb_uid," +
                   "pay_password,ad_text,push_cid,alipay_account,weixin_account," +
                   "ebank_account,id_card,occupation,credit_card,use_mobile_time) " +
                   "values(1,'%s','%s','','',"
                   "'','','','', %d,"
                   "1,0,0,0,%d,'','','%s',"
                   "'','','',0,'',0,'',"
                   "0,'',0,'',"
                   "'',0,0,'','','',"
                   "'','','','','',"
                   "'','',0,2,0)" % (tel, password, timestamp, timestamp, tel))
    cursor.close()
    return cursor.lastrowid
