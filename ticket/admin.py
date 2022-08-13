from django.contrib import admin
from django.db.models import Sum
from django.db.models.functions import Coalesce
from .models import Participant, Workshop
from django.utils.translation import gettext_lazy as _
#universal Model Admin
class CustomModelAdmin(admin.ModelAdmin):  
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.concrete_fields if field.name != "id"]
        super(CustomModelAdmin, self).__init__(model, admin_site)
class CustomWorkshopAdmin(admin.ModelAdmin):

    list_display = ['name','date','slot','participant_count']
    list_editable= ['slot']

    def participant_count(self, obj):       
        return obj.participant_set.aggregate(sum =Coalesce(Sum('quantity'),0))['sum']    
    participant_count.short_description = _('Số lượng vé đã đăng ký')

# Register your models here.
admin.site.register(Workshop,CustomWorkshopAdmin)
admin.site.register(Participant,CustomModelAdmin)