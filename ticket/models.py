from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Workshop(models.Model):
    name = models.CharField(verbose_name='Tên Workshop',max_length=30)
    date = models.DateTimeField(verbose_name='Ngày diễn ra')
    slot = models.IntegerField(verbose_name='Số lượng chỗ trống')
    class Meta:
        verbose_name = 'Workshop'
        verbose_name_plural = 'Workshop'

    def __str__(self):
        return self.name

class Participant(models.Model):
    workshop_id = models.ForeignKey(Workshop, on_delete= models.CASCADE,verbose_name='Workshop')
    user_id = models.ForeignKey(User, on_delete= models.CASCADE,verbose_name='Người dùng')
    date = models.DateTimeField(verbose_name ='Ngày tham gia',default= datetime.utcnow)
    quantity = models.IntegerField(verbose_name='Số lượng đăng ký',default= 1)

    class Meta:
        verbose_name = 'Người tham gia'
        verbose_name_plural = 'Người tham gia'

    def __str__(self):
        return ' '