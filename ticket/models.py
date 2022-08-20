from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

from ticket.methods import add_participant_to_google_sheet
# Create your models here.
class Workshop(models.Model):
    name = models.CharField(verbose_name=_('Tên Workshop'),max_length=30)
    date = models.DateTimeField(verbose_name=_('Ngày diễn ra'))
    slot = models.IntegerField(verbose_name=_('Số lượng chỗ trống'))
    class Meta:
        verbose_name = 'Workshop'
        verbose_name_plural = 'Workshop'

    def __str__(self):
        return self.name

class Participant(models.Model):
    workshop_id = models.ForeignKey(Workshop, on_delete= models.CASCADE,verbose_name='Workshop')
    user_id = models.ForeignKey(User, on_delete= models.CASCADE,verbose_name=_('Người dùng'))
    date = models.DateTimeField(verbose_name =_('Ngày tham gia'),default= datetime.utcnow)
    quantity = models.IntegerField(verbose_name=_('Số lượng đăng ký'),default= 1)
    qrcode = models.CharField(blank= True, max_length=254)

    class Meta:
        verbose_name = _('Người tham gia')
        verbose_name_plural = _('Người tham gia')

    def __str__(self):
        return ' '

@receiver(post_save,sender= Participant)
def post_save_participant(sender, instance, *args, **kwargs):
    user_info = {
        "timestamp": instance.date.timestamp(),
        "FullName": instance.user_id.last_name + ' ' + instance.user_id.first_name,
        "Birthday": instance.user_id.userextend.birthdate.strftime("%d/%m/%Y"),
        "PhoneNo": instance.user_id.userextend.phone_number,
        "Email": instance.user_id.email,
        "QRCode": instance.qrcode,
        "Workshop": instance.workshop_id.id,
        "CheckInStatus": "N",
        "Parish": instance.user_id.userextend.parish,
        "Address": instance.user_id.userextend.address,
        "Group": instance.quantity,
    }
    add_participant_to_google_sheet(user_info)
