from django.db import models


# Create your models here.

class Tag(models.Model):
    name = models.CharField(max_length=50)
    desc = models.TextField(blank=True)

    def __str__(self):
        return self.name
