from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.db.models.signals import post_delete

# Create your models here.
class UserExtend(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE,verbose_name='Người dùng')
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Xin vui lòng nhập đúng số điện thoại!")
    phone_number = models.CharField(verbose_name='Số điện thoại',validators=[phone_regex], max_length=17, blank=True)
    birthdate = models.DateField(verbose_name='Ngày sinh', default= datetime.now)
    address = models.CharField(verbose_name='Địa chỉ', blank=True, max_length=254)   
    parish = models.CharField(verbose_name='Giáo xứ', blank=True, max_length=100)
    ticket = models.IntegerField(verbose_name='Số vé',default=0)
    is_email_verified = models.BooleanField(verbose_name='Đã xác nhận Email',default= False)
    activation_key = models.CharField(verbose_name='Key kích hoạt',blank=True, max_length=40)
    key_expires = models.DateTimeField(verbose_name='Thời hạn key',blank = True,null=True)

    class Meta:
        verbose_name = 'Nhập vé'
        verbose_name_plural = 'Nhập vé'

    def __str__(self):
        return self.user_id.username

@receiver(post_delete, sender=UserExtend)
def post_delete_user(sender, instance, *args, **kwargs):
    if instance.user_id: # just in case user is not specified
        instance.user_id.delete()