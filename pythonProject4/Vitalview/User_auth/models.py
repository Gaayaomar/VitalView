from datetime import timezone

from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User ( AbstractUser ):
    email = models.EmailField ( unique=True )
    password = models.CharField ( max_length=128 )
    username = models.CharField ( max_length=128, default='' )
    role = models.CharField ( max_length=20 )
    age = models.IntegerField ( null=True, blank=True )
    sex = models.CharField ( max_length=10, null=True, blank=True )
    photo = models.ImageField ( upload_to='user_photos', null=True, blank=True )


    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []
    class Meta:
        db_table = 'users'

class vitalss(models.Model):
    a = models.IntegerField()
    b = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vitals')
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager ()  # default manager

    def __str__(self):
        return f"{self.a}, {self.b}"


class BlacklistToken(models.Model):
    objects = models.Manager ()
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    token = models.CharField(max_length=255)



class Assignment(models.Model):
    patient = models.ForeignKey('User',related_name='patient_assignments', on_delete=models.CASCADE)
    doctor = models.ForeignKey('User',  related_name='doctor_assignments',on_delete=models.CASCADE)
    assignment_date = models.DateField(auto_now_add=True)
    objects = models.Manager ()


class Appointment(models.Model):
    patient = models.ForeignKey('User',related_name='patient_appointement', on_delete=models.CASCADE)
    doctor = models.ForeignKey('User', related_name='docrtor_appointement', on_delete=models.CASCADE)
    start = models.DateTimeField ()
    end = models.DateTimeField ()
    approved = models.BooleanField(default=False)
    objects = models.Manager ()