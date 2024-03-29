from datetime import datetime
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.db.models.signals import pre_save,post_save,post_delete
from django.utils.translation import gettext_lazy as _
from ticket.methods import generate_qrcode, generate_ticket
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from ticket.models import Participant, Workshop
from users.methods import send_email, send_email_img

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
    ticket = models.IntegerField(verbose_name=_('Nhập vé thường'),default=0)
    input_special_ticket = models.PositiveIntegerField(verbose_name="Nhập vé ws", default = 0)
    special_ticket = models.IntegerField(verbose_name=_('Vé ws hiện có'),default=0)

    is_email_verified = models.BooleanField(verbose_name=_('Đã xác nhận Email'),default= False)
    activation_key = models.CharField(verbose_name=_('Key kích hoạt'),blank=True, max_length=40)
    key_expires = models.DateTimeField(verbose_name=_('Thời hạn key'),blank = True,null=True)
    language = models.CharField(verbose_name=_('Ngôn ngữ'),max_length=10,choices= settings.LANGUAGES, default=settings.LANGUAGE_CODE)

    def __str__(self):
        return self.user_id.username

    def clean(self):
        if self.ticket > 0:
            #check if user activate email
            if self.is_email_verified == False:
                raise ValidationError(_('Tài khoản {username} chưa xác nhận email.').format(username = self.user_id.username))
            #check if  normal workshop exists
            normal_workshop = Workshop.objects.filter(name='Normal Workshop', is_special = False).annotate(available = Coalesce(F('slot') - Sum('participant__quantity'),'slot')).first() 
            if not normal_workshop:
                raise ValidationError(_('"Normal Workshop" không tồn tại. Hãy tạo 1 Workshop tên "Normal Workshop", is_special = False'))
           #check if normal workshop slot still available
            if normal_workshop.available < self.ticket:
                raise ValidationError(_('Bạn chỉ có thể thêm {available} vé thường.').format(available = str(normal_workshop.available)))

        if self.input_special_ticket > 0:
            if self.is_email_verified == False:
                raise ValidationError(_('Tài khoản {username} chưa xác nhận email.').format(username = self.user_id.username))
            return super().clean()
            
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
         
        # Send Ticket to Email
        fullname = instance.user_id.last_name + ' ' + instance.user_id.first_name
        shortcode = fullname + ' ' + str(participant.quantity)
        fullcode = fullname + '\n' + str(participant.workshop_id.id) + '\n' + participant.qrcode + '\n' + 'ĐHGT ' + str(datetime.utcnow().year)

        # generate ticket
        byte_ticket_img = generate_ticket(fullcode,shortcode,normal_workshop.id,normal_workshop.ticket_template)
        #Send email function                   
        subject =_('VÉ THAM DỰ ĐẠI HỘI GIỚI TRẺ {year} của {last_name} {first_name}').format(year=str(datetime.utcnow().year),last_name=instance.user_id.last_name,first_name=instance.user_id.first_name)
        template = 'ticket/send_ticket_template.html'
        to_emails=[]
        to_emails.append(instance.user_id.email)
        bcc =[]
        bcc.append('dhgttgpsaigon@gmail.com')
        merge_data = {
            'fullname': instance.user_id.last_name + ' ' + instance.user_id.first_name,
            'workshop': normal_workshop.name,  
            'date':normal_workshop.date,
            'address':normal_workshop.address               
        }
        send_email_img(template,subject,to_emails,merge_data,byte_ticket_img,bcc=bcc)            

        instance.ticket = 0
        participant.save()  
        instance.save()

        # Logger
        Logger.info(f'{instance.user_id.username} registered {normal_workshop.name} ticket. Quantity: {participant.quantity}')
    
@receiver(post_save, sender=UserExtend)
def add_ws_ticket(sender,instance, *args, **kwargs):
    if instance.id:
        if instance.input_special_ticket > 0:
            # add special ticket
            instance.special_ticket += instance.input_special_ticket
            # minus all input to zero
            instance.input_special_ticket = 0
            instance.save()
            #Send email function                   
            subject = 'Xác nhận chuyển khoản!'
            template = 'users/notify_after_added_ticket_template.html'
            to_emails=[]
            to_emails.append(instance.user_id.email)
            merge_data = {
            'fullname': instance.user_id.last_name + ' ' + instance.user_id.first_name,
            'link_home': settings.DOMAIN_NAME,
            'link_guide': 'https://gioitresaigon.net/huong-dan-mua-ve-dhgt-2022.html',         
            }
            send_email(template,subject,to_emails,merge_data)         
            

@receiver(post_delete, sender = UserExtend)
def post_delete_user(sender, instance, *args, **kwargs):
    if instance.user_id: # just in case user is not specified
        instance.user_id.delete()