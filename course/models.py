from django.db import models

class Course(models.Model):
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=250)
    def __str__(self):
        return self.name

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=250)
    text = models.TextField()
    order = models.FloatField()
    release = models.DateTimeField()
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["order"]