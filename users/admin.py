from datetime import datetime, timedelta
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.core.mail import get_connection
from users.methods import random_string_generator, send_email
from users.models import UserExtend
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import logging

Logger = logging.getLogger("admin_ticket_log")
#universal Model Admin
class CustomModelAdmin(admin.ModelAdmin):  
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.concrete_fields if field.name != "id"]
        super(CustomModelAdmin, self).__init__(model, admin_site)
#Inline Class
class UserExtendInline(admin.StackedInline):
    model = UserExtend
    can_delete = False   
    
# class ParticipantInline(admin.TabularInline):
#     model = Participant
#     fields = ['workshop_id','quantity','date']
#     readonly_fields =['workshop_id','quantity','date']
#     ordering=['-date']
#     extra = 0
#     can_delete = False
#     verbose_name = _('Workshop đã đăng ký')
#     verbose_name_plural = _('Workshop đã đăng ký')

#Model Class
class CustomUser(User):
    class Meta:
        proxy = True
        verbose_name = _('Người dùng')
        verbose_name_plural = _('Người dùng')
class CustomUserAdmin(BaseUserAdmin):
    inlines = [UserExtendInline,]
    search_fields =['username','first_name','last_name','email']
    save_on_top = True
class CustomUserExtendAdmin(admin.ModelAdmin):
    list_display=['user_id','get_fullname','get_email','is_email_verified','ticket','get_selected_normal_ticket','input_special_ticket','special_ticket','get_selected_ws_ticket']
    search_fields=['user_id__username','user_id__last_name','user_id__first_name','phone_number','user_id__email']
    list_editable=['ticket','input_special_ticket']   
    actions=['send_multi_verify_email']

    def get_email(self,obj):
        email = obj.user_id.email
        return email
    get_email.short_description = 'email'

    def get_fullname(self, obj):
        fullname = obj.user_id.last_name + ' ' + obj.user_id.first_name
        return fullname
    get_fullname.short_description = _('Họ tên')

    def get_selected_normal_ticket(self, obj):
        quantity = obj.user_id.participant_set.filter(workshop_id__name ='Normal Workshop').aggregate(sum =Coalesce(Sum('quantity'),0))['sum']   
        return quantity
    get_selected_normal_ticket.short_description = _('Vé thường đã gửi')

    def get_selected_ws_ticket(self,obj):
        quantity = obj.user_id.participant_set.filter(workshop_id__is_special = True).aggregate(sum =Coalesce(Sum('quantity'),0))['sum'] 
        return quantity
    get_selected_ws_ticket.short_description='Vé ws đã gửi'

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': _('Nhập vé cho người dùng.')}
        return super(CustomUserExtendAdmin, self).changelist_view(request, extra_context=extra_context)

    def save_model(self, request, obj, form, change): 
        super().save_model(request, obj, form, change)      
        if 'ticket' in form.changed_data:
            Logger.info('{user} added {ticket} normal ticket(s) to {obj_username} and exported to {obj_username}\'s email.'.format(user = request.user, obj_username = obj.user_id.username ,ticket = form.cleaned_data.get('ticket')))
        if 'input_special_ticket' in form.changed_data:
            Logger.info('{user} added {input_special_ticket} Workshop ticket(s) to {obj_username}.'.format(user = request.user, obj_username = obj.user_id.username ,input_special_ticket = form.cleaned_data.get('input_special_ticket')))
        return 
    
    @admin.action(description='Gửi mail xác nhận cho nhiều Email')
    def send_multi_verify_email(self,request,queryset):
        for query in queryset:
            if not query.is_email_verified:
                query.activation_key = random_string_generator(length=15)
                query.key_expires = datetime.now() + timedelta(days=1)  
                query.save()         
                #Send mail to verify email function
                connection = get_connection(host=settings.GMAIL_HOST,port=settings.GMAIL_PORT,username=settings.GMAIL_HOST_USER, password=settings.GMAIL_HOST_PASSWORD,use_tls=settings.GMAIL_USE_TLS)
                subject =_('Xác nhận email!')
                template ='users/verify_email_template.html'
                verify_link = request.scheme + '://' + request.get_host() +'/u/confirm-email/' + query.activation_key
                home_link = settings.DOMAIN_NAME
                to_emails=[]
                to_emails.append(query.user_id.email)
                merge_data = {
                    'fullname':query.user_id.last_name + ' ' + query.user_id.first_name,
                    'verify_link':verify_link,
                    'home_link':home_link,
                }         
                send_email(template,subject,to_emails,merge_data,connection)
        self.message_user(request,'Đã gửi email.')
        


        
    
# Register your models
admin.site.unregister(User)
admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(UserExtend,CustomUserExtendAdmin)