import csv
from django.contrib import admin
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from .models import Participant, Workshop
from django.utils.translation import gettext_lazy as _
#universal Model Admin
class CustomModelAdmin(admin.ModelAdmin):  
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.concrete_fields if field.name != "id"]
        super(CustomModelAdmin, self).__init__(model, admin_site)
class CustomWorkshopAdmin(admin.ModelAdmin):

    list_display = ['name','date','slot','is_special','participant_count']
    list_editable= ['slot','is_special']
    search_fields = ['name']

    def participant_count(self, obj):       
        return obj.participant_set.aggregate(sum =Coalesce(Sum('quantity'),0))['sum']    
    participant_count.short_description = _('Số lượng vé đã đăng ký')

class CustomParticipantAdmin(admin.ModelAdmin):
    list_display = ['workshop_id','user_id','date','quantity','qrcode',]
    search_fields=['workshop_id__name','user_id__username','date']
    actions=['export_csv']

    @admin.action(description='Xuất dữ liệu ra csv')
    def export_csv(self,request,queryset):
        response = HttpResponse(content_type='text/csv')
        response ['Content-Disposition'] = 'attachment; filename="Participant.csv"'
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        # write header in csv
        writer.writerow(['timestamp','FullName','Birthday','PhoneNo','Email','QRCode','Workshop','CheckInStatus','Parish','Address','Group'])
        # get all participants data
        participants = Participant.objects.all()
        for participant in participants:
            item_array = []
            item_array.append(participant.date.timestamp())
            item_array.append(participant.user_id.last_name + ' ' + participant.user_id.first_name)
            item_array.append(participant.user_id.userextend.birthdate.strftime("%d/%m/%Y"))
            item_array.append(participant.user_id.userextend.phone_number)
            item_array.append(participant.user_id.email)
            item_array.append(participant.qrcode)
            item_array.append(participant.workshop_id.id)
            item_array.append("N")
            item_array.append(participant.user_id.userextend.parish)
            item_array.append(participant.user_id.userextend.address)
            item_array.append(participant.quantity)
            # write data to csv
            writer.writerow(item_array)    
        return response

# Register your models here.
admin.site.register(Workshop,CustomWorkshopAdmin)
admin.site.register(Participant,CustomParticipantAdmin)