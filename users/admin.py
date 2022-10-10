from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.forms import BaseModelFormSet
from ticket.models import Participant, Workshop
from users.models import UserExtend
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _
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

    def get_changelist_formset(self, request, **kwargs):
        kwargs['formset'] = UserExtendFormSet
        return super().get_changelist_formset(request, **kwargs)

class UserExtendFormSet(BaseModelFormSet):
    def clean(self):
        form_set = self.cleaned_data
        for form_data in form_set:        
            #check if normal ticket still have slot
            if int(form_data.get('ticket')) > 0:
                #check if email is verified
                if form_data.get('id').is_email_verified == False:
                    raise forms.ValidationError(_('Tài khoản {username} chưa xác nhận email.').format(username = form_data.get('id').user_id.username))

                #check if  normal workshop exists
                normal_workshop = Workshop.objects.filter(name='Normal Workshop', is_special = False).annotate(available = Coalesce(F('slot') - Sum('participant__quantity'),'slot')).first()             
                if not normal_workshop:
                    raise forms.ValidationError(_('Normal Workshop không tồn tại.'))
                    
                #check if normal workshop slot still available
                if normal_workshop.available < form_data.get('ticket'):
                    raise forms.ValidationError(_('Bạn chỉ có thể thêm {available} vé thường.').format(available = str(normal_workshop.available)))
        return form_set
    
# Register your models
admin.site.unregister(User)
admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(UserExtend,CustomUserExtendAdmin)