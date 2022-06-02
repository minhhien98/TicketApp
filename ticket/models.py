from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Workshop(models.Model):
    name = models.CharField(max_length=30)
    date = models.DateTimeField()
    slot = models.IntegerField()

class Participant(models.Model):
    workshop_id = models.ForeignKey(Workshop, on_delete= models.CASCADE)
    user_id = models.ForeignKey(User, on_delete= models.CASCADE)
    join_date = models.DateTimeField(default= datetime.utcnow)
