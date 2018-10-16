#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Author  : mofei
# @Time    : 2018/9/12 10:56
# @File    : extra_tags.py
# @Software: PyCharm
from django import template

register = template.Library()


@register.simple_tag
def get_display_page_range(num_pages, num, display_count=5):
    p = display_count // 2
    if num <= p:
        s = 1
        e = min(display_count, num_pages)
    elif num > num_pages -p:
        s = max(1, num_pages-display_count+1)
        e = num_pages
    else:
        s = max(num - p, 1)
        e = min(num + p, num_pages)
    # s = max(num - p, 1)
    # e = min(num + p, num_pages)
    # page_count = e - s + 1
    # if page_count < display_count:
    #     d = display_count - page_count
    #     if s > 1:
    #         s -= min(d, s - 1)
    #     elif e < num_pages:
    #         e += min(d, num_pages - e)
    return range(s, e + 1)


if __name__ == '__main__':
    num_pages = 10
    for num in range(1, num_pages + 1):
        print(num, get_display_page_range(num_pages, num))
