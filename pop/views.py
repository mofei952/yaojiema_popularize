import json
import random
import uuid

import datetime

import re
from django.contrib.auth.hashers import check_password, make_password
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from django.urls import reverse
from django.views import View
from pytz import utc

from pop import user_db, sms_api
from pop.decorators import login_required
from pop.forms import LoginForm, ChannelAccountAddForm, ChannelAccountEditForm, ChannelAccountModifyPasswordForm
from pop.models import Channel, ChannelAccount, ChannelOrder, Sms


def errors_to_msg(errors):
    """将error字典转化为字符串，只获取第一个错误"""
    error = ''
    for key, err_list in errors.items():
        for err in err_list:
            if err:
                error = err
                break
    return error


def response_success(data=None):
    """返回成功的Response"""
    return JsonResponse({'code': 'ACK', 'data': data})


def response_error(msg=None):
    """返回失败的response"""
    return JsonResponse({'code': 'NACK', 'msg': msg})


class LoginView(View):
    def get(self, request):
        """跳转到登录页面"""
        login_form = LoginForm()
        return render(request, 'login.html', {'form': login_form})

    def post(self, request):
        """ajax登录请求"""
        login_form = LoginForm(request.POST)
        if not login_form.is_valid():
            return response_error(errors_to_msg(login_form.errors))
        data = login_form.cleaned_data
        username = data.get('username')
        password = data.get('password')
        account = ChannelAccount.objects.filter(username=username).first()
        if not account or not check_password(password, account.password):
            return response_error('用户名或密码错误')
        if account.state == ChannelAccount.STOP:
            return response_error('账号被禁用')
        request.session['user'] = account.to_dict()
        return response_success()


class IndexView(View):
    @login_required()
    def get(self, request):
        """跳转到首页，admin跳转index，normal跳转channel-account-index"""
        level = request.session['user']['level']
        if level == 'ADMIN':
            return render(request, 'index.html')
        else:
            return render(request, 'channel-account-index.html')


class LogoutView(View):
    @login_required()
    def get(self, request):
        """登出，清除session"""
        request.session.clear()
        return redirect(reverse('login'))


class WelcomeView(View):
    @login_required()
    def get(self, request):
        """
            跳转到欢迎页，显示统计信息，
            若等级为admin，显示渠道数量，渠道账号数量，渠道订单数量，
            若等级为normal，只显示当前用户所属的渠道的订单数量
        """
        if request.session['user']['level'] == 'ADMIN':
            channel_count = Channel.objects.count()
            account_count = ChannelAccount.objects.count()
            order_count = ChannelOrder.objects.count()
            return render(request, 'welcome.html',
                          {'channel_count': channel_count, 'account_count': account_count, 'order_count': order_count})
        else:
            order_count = ChannelOrder.objects.filter(channel_id=request.session['user']['channel_id']).count()
            return render(request, 'welcome.html', {'order_count': order_count})


class ChannelListView(View):
    @login_required(admin=True)
    def get(self, request, page=1):
        """跳转到渠道列表页面，只有admin有权限"""
        channel_list = Channel.objects.order_by('-create_at')
        paginator = Paginator(channel_list, 15)
        channel_list = paginator.get_page(page)
        return render(request, 'channel-list.html', {'channel_list': channel_list})


class ChannelAddView(View):
    @login_required(admin=True)
    def get(self, request):
        """跳转到渠道添加页面"""
        return render(request, 'channel-add.html')

    @login_required(admin=True)
    def post(self, request):
        """ajax渠道添加处理"""
        name = request.POST.get('name')
        if not name:
            return response_error('渠道名称不能为空')
        if Channel.objects.filter(name=name):
            return response_error('渠道已存在')
        code = uuid.uuid4()
        Channel.objects.create(name=name, code=code)
        return response_success()


class ChannelEditView(View):
    @login_required(admin=True)
    def get(self, request, id):
        """跳转到渠道编辑页面"""
        channel = Channel.objects.get(id=id)
        return render(request, 'channel-edit.html', {'channel': channel})

    @login_required(admin=True)
    def post(self, request, id):
        """ajax渠道编辑处理"""
        name = request.POST.get('name')
        if not name:
            return response_error('渠道名称不能为空')
        if Channel.objects.filter(name=name):
            return response_error('渠道名称已被使用')
        Channel.objects.filter(id=id).update(name=name)
        return response_success()


class ChannelDeleteView(View):
    @login_required(admin=True)
    def post(self, request):
        """ajax渠道删除处理，可以批量"""
        ids = json.loads(request.POST.get('ids'))
        error_dict = {
            'has_account': [],
            'has_order': []
        }
        for id in ids:
            accounts = ChannelAccount.objects.filter(channel_id=id)
            orders = ChannelOrder.objects.filter(channel_id=id)
            if accounts or orders:
                channel = Channel.objects.get(id=id)
                if accounts:
                    error_dict['has_account'].append(channel.name)
                if orders:
                    error_dict['has_order'].append(channel.name)
        if error_dict['has_account'] or error_dict['has_order']:
            msg = ''
            if error_dict['has_account']:
                msg += ','.join(error_dict['has_account']) + '有渠道账号，不能删除<br>'
            if error_dict['has_order']:
                msg += ','.join(error_dict['has_order']) + '有渠道订单，不能删除'
            return response_error(msg)
        Channel.objects.filter(id__in=ids).delete()
        return response_success()


class ChannelAccountListView(View):
    @login_required(admin=True)
    def get(self, request, page=1):
        """跳转到渠道账号列表页面"""
        channel_account_list = ChannelAccount.objects.order_by('-create_at')
        paginator = Paginator(channel_account_list, 15)
        channel_account_list = paginator.get_page(page)
        return render(request, 'channel-account-list.html', {'channel_account_list': channel_account_list})


class ChannelAccountAddView(View):
    @login_required(admin=True)
    def get(self, request):
        """跳转到渠道账号添加页面"""
        channel_list = Channel.objects.order_by('-create_at')
        return render(request, 'channel-account-add.html', {'channel_list': channel_list})

    @login_required(admin=True)
    def post(self, request):
        """ajax渠道账号添加处理"""
        form = ChannelAccountAddForm(request.POST)
        if not form.is_valid():
            return response_error(errors_to_msg(form.errors))
        form.instance.password = make_password(form.instance.password)
        form.save()
        return response_success()


class ChannelAccountChangeStateView(View):
    @login_required(admin=True)
    def get(self, request, id, state):
        """ajax渠道账号修改状态处理"""
        if state not in (ChannelAccount.START, ChannelAccount.STOP):
            return response_error('状态错误')
        ChannelAccount.objects.filter(id=id).update(state=state)
        return response_success()


class ChannelAccountEditView(View):
    @login_required(admin=True)
    def get(self, request, id):
        """跳转到渠道账号编辑页面"""
        account = ChannelAccount.objects.get(id=id)
        channel_list = Channel.objects.order_by('-create_at')
        return render(request, 'channel-account-edit.html', {'account': account, 'channel_list': channel_list})

    @login_required(admin=True)
    def post(self, request, id):
        """ajax渠道账号编辑处理"""
        account = ChannelAccount.objects.get(id=id)
        if not account:
            return response_error('账号不存在')
        form = ChannelAccountEditForm(request.POST, instance=account)
        if not form.is_valid():
            return response_error(errors_to_msg(form.errors))
        form.save()
        return response_success()


class ChannelAccountModifyPasswordView(View):
    @login_required(admin=True)
    def get(self, request, id):
        """跳转到渠道账号修改密码页面"""
        account = ChannelAccount.objects.get(id=id)
        return render(request, 'channel-account-password.html', {'account': account})

    @login_required(admin=True)
    def post(self, request, id):
        """ajax渠道账号密码修改处理"""
        account = ChannelAccount.objects.get(id=id)
        if not account:
            return response_error('账号不存在')
        form = ChannelAccountModifyPasswordForm(request.POST, instance=account)
        if not form.is_valid():
            return response_error(errors_to_msg(form.errors))
        form.instance.password = make_password(form.instance.password)
        form.save()
        return response_success()


class ChannelAccountDeleteView(View):
    @login_required(admin=True)
    def post(self, request):
        """ajax渠道账号删除处理，可以批量"""
        ids = json.loads(request.POST.get('ids'))
        ChannelAccount.objects.filter(id__in=ids).delete()
        return response_success()


class ChannelOrderListView(View):
    def get(self, request, page=1):
        """跳转到渠道订单列表页面，可以根据时间范围和渠道名称进行筛选"""
        data = request.GET
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        channel_name = data.get('channel_name')
        dict_filter = {}
        if request.session['user']['level'] != 'ADMIN':
            dict_filter['channel__id'] = request.session['user'].get('channel_id')
        if start_date:
            dict_filter['create_at__gt'] = start_date
        if end_date:
            dict_filter['create_at__lt'] = datetime.datetime.strptime(end_date, "%Y-%m-%d") + datetime.timedelta(days=1)
        if channel_name:
            dict_filter['channel__name'] = channel_name
        channel_order_list = ChannelOrder.objects.filter(**dict_filter).order_by('-create_at')
        paginator = Paginator(channel_order_list, 15)
        channel_order_list = paginator.get_page(page)
        # 从user表查询对应的手机号码和真实姓名添加到订单对象中
        if channel_order_list:
            user_ids = [order.user_id for order in channel_order_list]
            user_list = user_db.get_by_ids(user_ids)
            user_id_and_user_dict = {user.get('id'): user for user in user_list}
            for order in channel_order_list:
                user = user_id_and_user_dict.get(order.user_id)
                order.tel = user.get('mobile')
                order.real_name = user.get('real_name')
        return render(request, 'channel-order-list.html', {'channel_order_list': channel_order_list})


class ChannelPromotionView(View):
    def get(self, request, code):
        """跳转到渠道推广页面"""
        channel = Channel.objects.filter(code=code).first()
        if not channel:
            return HttpResponse(status=404)
        return render(request, 'channel-promotion.html')

    def post(self, request, code):
        """ajax渠道推广页面注册处理"""
        tel = request.POST.get('tel')
        verification_code = request.POST.get('verification_code')
        # password = request.POST.get('password')
        channel = Channel.objects.filter(code=code).first()
        if not channel:
            return response_error('渠道code错误')
        # 检查手机号格式
        if not re.match(r'\d{11}$', tel):
            return response_error('手机号格式不正确')
        # 手机号已经注册
        if user_db.get_by_tel(tel):
            return response_error('用户已经存在')
        # 判断短信是否发送
        sms = Sms.objects.filter(tel=tel).order_by('-send_time').first()
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        if not sms or sms.state == Sms.SEND_FAIL:
            return response_error('短信未发送')
        # 判断当前时间时间是否超过短信有效时间
        if now > sms.valid_time:
            return response_error('验证码已失效')
        # 判断是否验证过于频繁
        if sms.verification_time and now - sms.verification_time < datetime.timedelta(seconds=5):
            return response_error('验证过于频繁，请稍后再进行验证')
        # 验证 验证码 是否正确
        if sms.verification_code != verification_code:
            sms.verification_time = now
            sms.state = Sms.VERIFICATION_FAIL  # 修改短信状态为验证失败
            sms.save()
            return response_error('验证码错误，请5秒后重新验证')
        # 添加用户
        user_id = user_db.add_user(tel)
        # 添加渠道订单
        ChannelOrder.objects.create(channel=channel, user_id=user_id)
        # 修改短信状态为验证成功
        sms.state = Sms.VERIFICATION_SUCCESS
        sms.save()
        return response_success()


class SendVerificationCodeSmsView(View):
    def post(self, request):
        """ajax渠道推广页面短信验证码发送"""
        tel = request.POST.get('tel')
        # 检查手机号格式
        if not re.match(r'\d{11}$', tel):
            return response_error('手机号格式不正确')
        # 手机号已经注册
        if user_db.get_by_tel(tel):
            return response_error('用户已经存在')
        # 查出最近这个手机号码最近发送的短信，若发送时间和现在时间差小于60秒，返回错误
        sms = Sms.objects.filter(tel=tel).order_by('-send_time').first()
        if sms and datetime.datetime.utcnow().replace(tzinfo=utc) - sms.send_time < datetime.timedelta(seconds=60):
            return response_error('两次发送验证码间隔小于60秒')
        # 生成验证码，短信内容
        verification_code = '%06d' % random.randint(0, 999999)
        text = '您的验证码是%s' % verification_code
        state = Sms.SEND_FAIL
        # 调用发送短信接口，判断是否发送成功，修改state
        # response = sms_api.send_sms(text, tel)
        response = b'20110725160412,0\n1234567890100'  # TODO 暂时模拟成功结果
        result = re.split(r'\\n|,', str(response.decode('utf-8')))
        if result[1] == '0':
            state = Sms.SEND_SUCCESS
        # 存入数据库以便验证时比较
        now = datetime.datetime.now()
        Sms.objects.create(tel=tel, verification_code=verification_code, send_time=now,
                           valid_time=now + datetime.timedelta(minutes=5), state=state)
        return response_success()
