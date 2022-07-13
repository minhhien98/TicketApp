from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from ticket.models import Participant
from users.models import UserExtend
from django.db.models.functions import Coalesce
from django.db.models import Sum, Count,OuterRef

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
    verbose_name = 'Workshop đã đăng ký'
    verbose_name_plural = 'Workshop đã đăng ký'

#Model Class
class CustomUser(User):
    class Meta:
        proxy = True
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Người dùng'
class CustomUserAdmin(BaseUserAdmin):
    inlines = [UserExtendInline,ParticipantInline,]
    save_on_top = True
class CustomUserExtendAdmin(admin.ModelAdmin):
    list_display=['user_id','phone_number','birthdate','ticket','address','parish']
    list_editable=['ticket']   

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Nhập vé cho người dùng.'}
        return super(CustomUserExtendAdmin, self).changelist_view(request, extra_context=extra_context)
    
# Register your models
admin.site.unregister(User)
admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(UserExtend,CustomUserExtendAdmin)