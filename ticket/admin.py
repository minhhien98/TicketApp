from django.contrib import admin

from .models import Participant, Workshop

# Register your models here.
admin.site.register(Workshop)
admin.site.register(Participant)