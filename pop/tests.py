import re

from django.contrib.auth.hashers import make_password
from django.test import TestCase, Client

# Create your tests here.
from pop.models import ChannelAccount, Channel


class TestSmsResponse(TestCase):
    def test(self):
        response = b'20110725160412,0'.decode('utf-8')
        result = re.split(r'\\n|,', str(response))
        self.assertEquals(result[1], '0')


class ChannelListTestCase(TestCase):
    def setUp(self):
        self.user = ChannelAccount(username='admin', category='ADMIN', password=make_password('123456'))
        self.user.save()
        # 模拟登陆
        self.client.post('/login', {'username': 'admin', 'password': '123456'})

        channel = Channel(name='123', code='11111')
        channel.save()

    def test(self):
        rep = self.client.get("/channel_list")
        self.assertEqual(rep.status_code, 200)
        for channel in rep.context['channel_list']:
            print(channel.name, channel.code)