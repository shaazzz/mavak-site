import jdatetime
from django.db import models
from django_jalali.db import models as jmodels

from main.models import Tag
from users.models import Collection


class Course(models.Model):
    link = "ویرایش"
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

    # release = models.DateTimeField()
    # drop_off_date = models.DateField()

    def __str__(self):
        return self.course.name + " " + self.name + " " + self.title

    class Meta:
        ordering = ["order"]


class CollectionLesson(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    start = jmodels.jDateTimeField(default=jdatetime.datetime.now().replace(hour=8, minute=0, second=0, microsecond=0))
    end = jmodels.jDateTimeField(default=jdatetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))

    def __str__(self):
        return self.collection.name + " " + str(self.lesson.name)

    class Meta:
        ordering = ["start"]
