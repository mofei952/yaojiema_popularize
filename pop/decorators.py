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
            if 'user' not in request.session:
                # return render(request, 'login.html', status='401')
                return redirect(reverse('login'))
            if admin and request.session['user']['level'] != 'ADMIN':
                return redirect(reverse('login'))
            return func(*args, **kwargs)
        return inner
    return login_require
