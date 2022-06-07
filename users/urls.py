

from . import views
from django.urls import path


app_name = 'users'
urlpatterns = [
    path('login/', views.login, name = 'login'),
    path('logout/', views.logout, name ='logout'),
    path('register/', views.register, name ='register'),
    path('register_success/', views.register_success, name ='register_success'),
    path('profile/',views.user_profile,name="user_profile"),
    path('change-password/',views.change_password,name="change_password")
]