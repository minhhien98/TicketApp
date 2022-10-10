from datetime import datetime, timedelta, timezone
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.db.models.signals import post_save,post_delete
from django.utils.translation import gettext_lazy as _
from ticket.methods import generate_qrcode, generate_ticket

from ticket.models import Participant, Workshop
from users.methods import send_email_img

import logging
Logger = logging.getLogger("workshop_log")

# Create your models here.
class UserExtend(models.Model):
    class Meta:
        verbose_name = _('Nhập vé')
        verbose_name_plural = _('Nhập vé')

    user_id = models.OneToOneField(User, on_delete=models.CASCADE,verbose_name=_('Người dùng'))
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=_("Xin vui lòng nhập đúng số điện thoại!"))
    phone_number = models.CharField(verbose_name=_('Số điện thoại'),validators=[phone_regex], max_length=17, blank=True)
    birthdate = models.DateField(verbose_name=_('Ngày sinh'), default= datetime.now)
    address = models.CharField(verbose_name=_('Địa chỉ'), blank=True, max_length=254)   
    parish = models.CharField(verbose_name=_('Giáo xứ'), blank=True, max_length=100)
    ticket = models.IntegerField(verbose_name=_('Vé thường'),default=0)
    special_ticket = models.IntegerField(verbose_name=_('Vé đặc biệt'),default=0)

    is_email_verified = models.BooleanField(verbose_name=_('Đã xác nhận Email'),default= False)
    activation_key = models.CharField(verbose_name=_('Key kích hoạt'),blank=True, max_length=40)
    key_expires = models.DateTimeField(verbose_name=_('Thời hạn key'),blank = True,null=True)
    language = models.CharField(verbose_name=_('Ngôn ngữ'),max_length=10,choices= settings.LANGUAGES, default=settings.LANGUAGE_CODE)

    def __str__(self):
        return self.user_id.username
@receiver(post_save,sender = UserExtend)
def send_normal_ticket(sender,instance,*args, **kwargs):
    #if normal workshop doesnt exist, create one
    normal_workshop = Workshop.objects.filter(name='Normal Workshop',is_special = False).first()
    if not normal_workshop:
        return

    if instance.ticket > 0:
        #add participant to normal workshop
        qrcode = generate_qrcode()
        participant = Participant(workshop_id = normal_workshop,user_id = instance.user_id,quantity = instance.ticket,qrcode = qrcode)
        participant.save()   
        # Send Ticket to Email
        fullname = instance.user_id.last_name + ' ' + instance.user_id.first_name
        shortcode = fullname + ' ' + participant.workshop_id.name + ' ' + str(participant.quantity)
        fullcode = fullname + '\n' + str(participant.workshop_id.id) + '\n' + participant.qrcode + '\n' + 'ĐHGT ' + str(datetime.utcnow().year)

        # generate ticket
        byte_ticket_img = generate_ticket(fullcode,shortcode,normal_workshop.id,normal_workshop.ticket_template)
        #Send email function                   
        subject =_('VÉ THAM DỰ ĐẠI HỘI GIỚI TRẺ {year} của {last_name} {first_name}').format(year=str(datetime.utcnow().year),last_name=instance.user_id.last_name,first_name=instance.user_id.first_name)
        template = 'ticket/send_ticket_template.html'
        merge_data = {
            'fullname': instance.user_id.last_name + ' ' + instance.user_id.first_name,
            'workshop': normal_workshop.name,  
            'date':normal_workshop.date,
            'address':normal_workshop.address               
        }
        send_email_img(template,subject,instance.user_id.email,merge_data,byte_ticket_img)            

        instance.ticket = 0
        instance.save()

        # Logger
        Logger.info(f'{instance.user_id.username} registered {normal_workshop.name} ticket. Quantity: {participant.quantity}')

@receiver(post_delete, sender = UserExtend)
def post_delete_user(sender, instance, *args, **kwargs):
    if instance.user_id: # just in case user is not specified
        instance.user_id.delete()