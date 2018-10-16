from django.db import models


class TimeStampModel(models.Model):
    create_at = models.DateTimeField(u'生成时间', auto_now_add=True)
    update_at = models.DateTimeField(u'修改时间', auto_now=True)

    class Meta:
        abstract = True


# class Admin(TimeStampModel):
#     username = models.CharField(max_length=50, unique=True)
#     password = models.CharField(max_length=255, unique=True)
#
#     def to_dict(self):
#         return {'id': self.id, 'name': self.username}


class Channel(TimeStampModel):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=255, unique=True)


class ChannelAccount(TimeStampModel):
    START = 'START'
    STOP = 'STOP'
    STATE_CHOICES = (
        (START, '已启用'),
        (STOP, '已停用'),
    )
    NORMAL = 'NORMAL'
    ADMIN = 'ADMIN'
    LEVEL_CHOICES = (
        (NORMAL, '普通账户'),
        (ADMIN, '管理员账户'),
    )
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    real_name = models.CharField(max_length=50)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default=NORMAL)
    channel = models.ForeignKey(Channel, models.CASCADE, null=True)
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default=START)

    def to_dict(self):
        return {'id': self.id, 'username': self.username, 'real_name': self.real_name,
                'level': self.level, 'channel_id': self.channel.id if self.channel else ''}


class ChannelOrder(TimeStampModel):
    channel = models.ForeignKey(Channel, models.CASCADE)
    user_id = models.IntegerField()


class Sms(TimeStampModel):
    SEND_FAIL = 'SEND_FAIL'
    SEND_SUCCESS = 'SEND_SUCCESS'
    VERIFICATION_FAIL = 'VERIFICATION_FAIL'
    VERIFICATION_SUCCESS = 'VERIFICATION_SUCCESS'
    STATE_CHOICES = (
        (SEND_FAIL, '发送失败'),
        (SEND_SUCCESS, '发送成功'),
        (VERIFICATION_FAIL, '验证失败'),
        (VERIFICATION_FAIL, '验证成功'),
    )
    tel = models.CharField(max_length=50)
    verification_code = models.CharField(max_length=10)
    send_time = models.DateTimeField()
    valid_time = models.DateTimeField()
    verification_time = models.DateTimeField(null=True)
    state = models.CharField(max_length=50)
