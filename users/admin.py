from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from ticket.models import Participant
from users.models import UserExtend
from django.db.models import Sum
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
    
class ParticipantInline(admin.TabularInline):
    model = Participant
    fields = ['workshop_id','quantity','date']
    readonly_fields =['workshop_id','quantity','date']
    ordering=['-date']
    extra = 0
    can_delete = False
    verbose_name = _('Workshop đã đăng ký')
    verbose_name_plural = _('Workshop đã đăng ký')

#Model Class
class CustomUser(User):
    class Meta:
        proxy = True
        verbose_name = _('Người dùng')
        verbose_name_plural = _('Người dùng')
class CustomUserAdmin(BaseUserAdmin):
    inlines = [UserExtendInline,ParticipantInline,]
    save_on_top = True
class CustomUserExtendAdmin(admin.ModelAdmin):
    list_display=['user_id','get_fullname','ticket','get_registered_ticket']
    list_editable=['ticket']   

    def get_fullname(self, obj):
        fullname = obj.user_id.last_name + obj.user_id.first_name
        return fullname
    get_fullname.short_description = _('Họ tên')

    def get_registered_ticket(self, obj):
        quantity = obj.user_id.participant_set.aggregate(sum =Coalesce(Sum('quantity'),0))['sum']   
        return quantity
    get_registered_ticket.short_description = _('Số vé đã đăng ký')

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': _('Nhập vé cho người dùng.')}
        return super(CustomUserExtendAdmin, self).changelist_view(request, extra_context=extra_context)
    
# Register your models
admin.site.unregister(User)
admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(UserExtend,CustomUserExtendAdmin)