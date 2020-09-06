from django.db import models
from django.utils import timezone
from datetime import datetime

from main.models import Tag


class Course(models.Model):
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Tag(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=250)
    text = models.TextField()
    order = models.FloatField()
    release = models.DateTimeField()
    drop_off_date = models.DateField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["order"]
