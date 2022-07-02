from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from ticket.models import Participant
from users.models import UserExtend

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
    readonly_fields =['workshop_id','date','quantity']
    ordering = ['-date',]
    extra = 0
    can_delete = False
    verbose_name = 'Lịch sử đăng ký workshop'
    verbose_name_plural = 'Lịch sử đăng ký workshop'

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
    list_display=['user_id','phone_number','birth_date','ticket','address','parish']
    list_editable=['ticket']   
    
# Register your models
admin.site.unregister(User)
admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(UserExtend,CustomUserExtendAdmin)