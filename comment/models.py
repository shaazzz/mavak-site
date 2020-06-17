from django.db import models
from django.contrib.auth.models import User

class Comment(models.Model):
    class Meta:
        ordering = ["-date"]
    date = models.DateTimeField(auto_now = True)
    sender = models.ForeignKey(User, on_delete= models.CASCADE)
    parent = models.ForeignKey('self', on_delete= models.CASCADE, blank=True, null= True)
    text = models.TextField()
    root = models.CharField(max_length=250)
