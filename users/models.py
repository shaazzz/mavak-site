from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ostan = models.CharField(max_length=50)
    shomare = models.CharField(max_length=50)
    dore = models.IntegerField(default=1)
    def __str__(self):
        return self.user.username

class Org(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ostan = models.CharField(max_length=50)
    shomare = models.CharField(max_length=50)
    title = models.CharField(max_length=250)
    GOONE_CHOICES = (
        ('D', 'دبیرستان (متوسطه دوره دوم)'),
        ('R', 'راهنمایی (متوسطه دوره اول)'),
        ('S', 'مرکز سمپاد'),
    )
    goone = models.CharField(max_length=1, choices=GOONE_CHOICES)
    verified = models.BooleanField(default= False)

