"""yaojiema_popularize URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.conf.urls import url, static
from django.urls import path

from pop import views
from yaojiema_popularize import settings

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('login', views.LoginView.as_view(), name='login'),
    path('', views.IndexView.as_view(), name='index'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('welcome', views.WelcomeView.as_view(), name='welcome'),
    path('channel_list', views.ChannelListView.as_view(), name='channel_list'),
    path('channel_list/<int:page>', views.ChannelListView.as_view(), name='channel_list'),
    path('channel_add', views.ChannelAddView.as_view(), name='channel_add'),
    path('channel_edit/<int:id>', views.ChannelEditView.as_view(), name='channel_edit'),
    path('channel_delete', views.ChannelDeleteView.as_view(), name='channel_delete'),

    path('channel_account_list', views.ChannelAccountListView.as_view(), name='channel_account_list'),
    path('channel_account_list/<int:page>', views.ChannelAccountListView.as_view(), name='channel_account_list'),
    path('channel_account_add', views.ChannelAccountAddView.as_view(), name='channel_account_add'),
    path('channel_account_change_state/<int:id>/<str:state>', views.ChannelAccountChangeStateView.as_view(), name='channel_account_change_state'),
    path('channel_account_edit/<int:id>', views.ChannelAccountEditView.as_view(), name='channel_account_edit'),
    path('channel_account_modify_password/<int:id>', views.ChannelAccountModifyPasswordView.as_view(), name='channel_account_modify_password'),
    path('channel_account_delete', views.ChannelAccountDeleteView.as_view(), name='channel_account_delete'),

    path('channel_order_list', views.ChannelOrderListView.as_view(), name='channel_order_list'),
    path('channel_order_list/<int:page>', views.ChannelOrderListView.as_view(), name='channel_order_list'),

    path('channel_promotion/<str:code>', views.ChannelPromotionView.as_view(), name='channel_promotion'),
    path('send_verification_code_sms', views.SendVerificationCodeSmsView.as_view(), name='send_verification_code_sms'),

    path('jump', views.jump, name='jump'),
]


if settings.DEBUG is False:
    # urlpatterns += url(r'^media/(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT}, name='media'),
    urlpatterns += url(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT }, name='static'),
else:
    # urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    pass