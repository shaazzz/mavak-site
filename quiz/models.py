from django.db import models
from django_jalali.db import models as jmodels

from main.models import Tag
from users.models import Student, Collection


class Quiz(models.Model):
    link = "ویرایش"
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=250)
    desc = models.TextField(default=None, blank=True, null=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='qtag')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)


class CollectionQuiz(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    multiple = models.FloatField(default=1)
    expectedScore = models.IntegerField(default=0)
    start = jmodels.jDateTimeField()
    end = jmodels.jDateTimeField()

    def __str__(self):
        return self.collection.name + " " + str(self.quiz.name)

    class Meta:
        ordering = ["start"]


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.TextField()
    order = models.IntegerField()
    typ = models.CharField(max_length=50)
    hint = models.TextField()
    mxgrade = models.IntegerField()

    def __str__(self):
        return self.quiz.name + " " + str(self.order)

    class Meta:
        ordering = ["order"]


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    text = models.TextField()
    grade = models.IntegerField()
    grademsg = models.CharField(max_length=200)

    def __str__(self):
        return str(self.question) + " " + str(self.student) + " score: " + str(self.grade)


class Secret(models.Model):
    key = models.CharField(max_length=50)
    value = models.TextField()

    def __str__(self):
        return self.key


class RateColor(models.Model):
    key = models.CharField(max_length=50)
    startValue = models.IntegerField()
    endValue = models.IntegerField()
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    labelColor = models.CharField(max_length=50)

    def __str__(self):
        return self.name
