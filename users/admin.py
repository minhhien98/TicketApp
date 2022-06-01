from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from users.models import UserExtend

# Register your models here.
#universal Model Admin
class CustomModelAdmin(admin.ModelAdmin):  
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.concrete_fields if field.name != "id"]
        super(CustomModelAdmin, self).__init__(model, admin_site)

class UserExtendInline(admin.StackedInline):
    model = UserExtend
    can_delete = False
    verbose_name_plural = 'user_extend'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserExtendInline,)
# Register your models
admin.site.unregister(User)
admin.site.register(User,UserAdmin)
admin.site.register(UserExtend,CustomModelAdmin)