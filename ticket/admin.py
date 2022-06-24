from django.contrib import admin
from .models import Participant, Workshop

#universal Model Admin
class CustomModelAdmin(admin.ModelAdmin):  
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.concrete_fields if field.name != "id"]
        super(CustomModelAdmin, self).__init__(model, admin_site)
class CustomWorkshopAdmin(admin.ModelAdmin):

    list_display = ['name','date','slot','participant_count']
    list_editable= ['slot']

    def participant_count(self, obj):
        return obj.participant_set.count()
    participant_count.short_description = ' Participants'

# Register your models here.
admin.site.register(Workshop,CustomWorkshopAdmin)
admin.site.register(Participant,CustomModelAdmin)