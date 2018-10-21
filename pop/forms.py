#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Author  : mofei
# @Time    : 2018/10/12 20:11
# @File    : forms.py
# @Software: PyCharm

from django import forms
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError

from pop.models import ChannelAccount, Channel


class LoginForm(forms.ModelForm):
    class Meta:
        model = ChannelAccount
        fields = ('username', 'password')
        error_messages = {
            'username': {
                'required': '用户名不能为空'
            },
            'password': {
                'required': '密码不能为空'
            }
        }

    def clean(self):
        # self._validate_unique = False
        return self.cleaned_data


class ChannelAccountAddForm(forms.ModelForm):
    class Meta:
        model = ChannelAccount
        fields = ('username', 'password', 'real_name', 'channel')


class ChannelAccountEditForm(forms.ModelForm):
    channel = forms.ModelChoiceField(Channel.objects, required=False)

    class Meta:
        model = ChannelAccount
        fields = ('real_name', 'channel')


class ChannelAccountModifyPasswordForm(forms.ModelForm):
    old_password = forms.CharField(max_length=255)

    class Meta:
        model = ChannelAccount
        fields = ('password',)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not check_password(old_password, self.instance.password):
            raise ValidationError('旧密码错误')
        return old_password
