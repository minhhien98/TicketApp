from django.urls import path
from . import views

app_name = 'ticket'
urlpatterns = [
    path('', views.home, name = 'home'),
    path('detail/<int:id>', views.ticket_detail, name = 'ticket_detail'),
    path('join-workshop/',views.join_workshop, name ='join_workshop')
]