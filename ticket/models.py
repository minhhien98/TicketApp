from datetime import datetime
from genericpath import isfile
import os
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from django_resized import ResizedImageField
#from users.methods import add_participant_to_google_sheet

# Create your models here.
class Workshop(models.Model):
    name = models.CharField(verbose_name=_('Tên Workshop'),max_length=30)
    date = models.DateTimeField(verbose_name=_('Ngày diễn ra'))
    slot = models.IntegerField(verbose_name=_('Số lượng chỗ trống'))
    is_special = models.BooleanField(verbose_name=_('Workshop đặc biệt'),default= False)
    address = models.CharField(verbose_name=_('Địa chỉ'),max_length=254, blank=False, default='')
    ticket_template = ResizedImageField(verbose_name=_('Ảnh vé'),upload_to='ticket/ticket_template',null=False, size=[720,1280])
    icon = ResizedImageField(verbose_name='icon',upload_to='ticket/icon',null=False, size=[90,90])

    intro_link = models.URLField(verbose_name=_('Link giới thiệu'),blank=True)
    class Meta:
        verbose_name = 'Workshop'
        verbose_name_plural = 'Workshop'

    def __str__(self):
        return self.name

class Participant(models.Model):
    workshop_id = models.ForeignKey(Workshop, on_delete= models.CASCADE,verbose_name='Workshop')
    user_id = models.ForeignKey(User, on_delete= models.CASCADE,verbose_name=_('Người dùng'))
    date = models.DateTimeField(verbose_name =_('Ngày tham gia'),default= datetime.now())
    quantity = models.IntegerField(verbose_name=_('Số lượng đăng ký'),default= 1)
    qrcode = models.CharField(blank= True, max_length=254)

    class Meta:
        verbose_name = _('Người tham gia')
        verbose_name_plural = _('Người tham gia')

    def __str__(self):
        return ' '

# Signal
# @receiver(post_save,sender= Participant)
# def post_save_participant(sender, instance, *args, **kwargs):
#     user_info = {
#         "timestamp": instance.date.timestamp(),
#         "FullName": instance.user_id.last_name + ' ' + instance.user_id.first_name,
#         "Birthday": instance.user_id.userextend.birthdate.strftime("%d/%m/%Y"),
#         "PhoneNo": instance.user_id.userextend.phone_number,
#         "Email": instance.user_id.email,
#         "QRCode": instance.qrcode,
#         "Workshop": instance.workshop_id.id,
#         "CheckInStatus": "N",
#         "Parish": instance.user_id.userextend.parish,
#         "Address": instance.user_id.userextend.address,
#         "Group": instance.quantity,
#     }
#     add_participant_to_google_sheet(user_info)

# These two auto-delete files from filesystem when they are unneeded:
@receiver(models.signals.post_delete, sender=Workshop)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    # delete template when delete workshop
    if instance.ticket_template:
        if os.path.isfile(instance.ticket_template.path):
            os.remove(instance.ticket_template.path)
    # delete icon when delete workshop
    if instance.icon:
        if os.path.isfile(instance.icon.path):
            os.remove(instance.icon.path)

@receiver(models.signals.pre_save, sender=Workshop)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = Workshop.objects.get(pk=instance.pk).ticket_template
        old_icon = Workshop.objects.get(pk=instance.pk).icon
    except Workshop.DoesNotExist:
        return False

    new_file = instance.ticket_template
    new_icon = instance.icon
    # change workshop template
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
    # change icon
    if not old_icon == new_icon:
        if os.path.isfile(old_icon.path):
            os.remove(old_icon.path)
    
