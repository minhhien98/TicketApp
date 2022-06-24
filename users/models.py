from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.db.models.signals import post_delete

from ticket.models import Participant, Workshop
# Create your models here.
class UserExtend(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Xin vui lòng nhập đúng số điện thoại!")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    birth_date = models.DateField(default= datetime.now)
    address = models.CharField(max_length=254)   
    parish = models.CharField(max_length=100)
    ticket = models.IntegerField(default=0)
    is_email_verified = models.BooleanField(default= False)
    activation_key = models.CharField(blank=True, max_length=40)
    key_expires = models.DateTimeField(blank = True,null=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return self.user_id.username

@receiver(post_delete, sender=UserExtend)
def post_delete_user(sender, instance, *args, **kwargs):
    if instance.user_id: # just in case user is not specified
        instance.user_id.delete()