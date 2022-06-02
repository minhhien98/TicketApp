from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
# Create your models here.
class UserExtend(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Xin vui lòng nhập đúng số điện thoại!")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    birth_date = models.DateField(default= datetime.now)
    address = models.CharField(max_length=254)   
    parish = models.CharField(max_length=100)
    ticket = models.IntegerField(default=0)
