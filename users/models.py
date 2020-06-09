from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ostan = models.CharField(max_length=50)
    def __str__(self):
        return self.user.username
