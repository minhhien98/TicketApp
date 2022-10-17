from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.forms import BaseModelFormSet
from ticket.models import Workshop
from users.models import UserExtend
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _
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
    list_display=['user_id','get_fullname','phone_number','ticket','special_ticket','get_selected_ticket']
    search_fields=['user_id__username','user_id__last_name','user_id__first_name','phone_number','user_id__email']
    list_editable=['ticket','special_ticket']   

    def has_add_permission(self, request):
        return False

    def get_fullname(self, obj):
        fullname = obj.user_id.last_name + obj.user_id.first_name
        return fullname
    get_fullname.short_description = _('Họ tên')

    def get_selected_ticket(self, obj):
        quantity = obj.user_id.participant_set.aggregate(sum =Coalesce(Sum('quantity'),0))['sum']   
        return quantity
    get_selected_ticket.short_description = _('Vé đã chọn')

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': _('Nhập vé cho người dùng.')}
        return super(CustomUserExtendAdmin, self).changelist_view(request, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if 'ticket' in form.changed_data:
            Logger.info('{user} added {ticket} normal ticket(s) to {obj_username} and exported to {obj_username}\'s email.'.format(user = request.user, obj_username = obj.user_id.username ,ticket = form.cleaned_data.get('ticket')))
        if 'special_ticket' in form.changed_data:
            Logger.info('{user} changed {obj_username}\'s Workshop ticket from {old_ticket} to {new_ticket}.'.format(user = request.user, obj_username = obj.user_id.username ,old_ticket = form.initial.get('special_ticket'), new_ticket = obj.special_ticket))
        return 
        
    
# Register your models
admin.site.unregister(User)
admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(UserExtend,CustomUserExtendAdmin)