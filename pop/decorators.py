#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Author  : mofei
# @Time    : 2018/9/10 18:52
# @File    : decorators.py
# @Software: PyCharm
from django.shortcuts import redirect, render
from django.urls import reverse

from pop.middleware import current_request


def login_required(admin=False):
    def login_require(func):
        def inner(*args, **kwargs):
            request = current_request()
            # 未登录跳回登录页面
            if 'user' not in request.session:
                # return render(request, 'login.html', status='401')
                return redirect(reverse('login'))
            # 若当前url访问需要admin权限但当前用户不是admin等级则跳回登录页面
            if admin and request.session['user']['level'] != 'ADMIN':
                return redirect(reverse('login'))
            return func(*args, **kwargs)
        return inner
    return login_require
