from datetime import datetime
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.utils.translation import gettext_lazy as _

# Create your models here.
class UserExtend(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE,verbose_name=_('Người dùng'))
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=_("Xin vui lòng nhập đúng số điện thoại!"))
    phone_number = models.CharField(verbose_name=_('Số điện thoại'),validators=[phone_regex], max_length=17, blank=True)
    birthdate = models.DateField(verbose_name=_('Ngày sinh'), default= datetime.now)
    address = models.CharField(verbose_name=_('Địa chỉ'), blank=True, max_length=254)   
    parish = models.CharField(verbose_name=_('Giáo xứ'), blank=True, max_length=100)
    ticket = models.IntegerField(verbose_name=_('Số vé'),default=0)

    is_email_verified = models.BooleanField(verbose_name=_('Đã xác nhận Email'),default= False)
    activation_key = models.CharField(verbose_name=_('Key kích hoạt'),blank=True, max_length=40)
    key_expires = models.DateTimeField(verbose_name=_('Thời hạn key'),blank = True,null=True)
    language = models.CharField(verbose_name=_('Ngôn ngữ'),max_length=10,choices= settings.LANGUAGES, default=settings.LANGUAGE_CODE)

    class Meta:
        verbose_name = _('Nhập vé')
        verbose_name_plural = _('Nhập vé')

    def __str__(self):
        return self.user_id.username

@receiver(post_delete, sender=UserExtend)
def post_delete_user(sender, instance, *args, **kwargs):
    if instance.user_id: # just in case user is not specified
        instance.user_id.delete()