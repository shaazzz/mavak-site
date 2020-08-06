from django.db import models
from users.models import Student
from datetime import datetime

class Quiz(models.Model):
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=250)
    start = models.DateTimeField(default= datetime.now)
    end   = models.DateTimeField(default= datetime.now)
    def __str__(self):
        return self.name

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.TextField()
    order = models.IntegerField()
    typ = models.CharField(max_length=50)
    hint = models.TextField()
    mxgrade = models.IntegerField()
    def __str__(self):
        return self.quiz.name+" "+str(self.order)
    class Meta:
        ordering = ["order"]

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    text = models.TextField()
    grade = models.IntegerField()
    grademsg = models.TextField()
    