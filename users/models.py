import uuid

from django.contrib.auth.models import User
from django.db import models

from main.models import Tag


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    return "%s.%s" % (uuid.uuid4(), ext)


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ostan = models.CharField(max_length=50)
    shomare = models.CharField(max_length=50)
    dore = models.IntegerField(default=1)
    verified = models.IntegerField(default=0)
    shenasname = models.ImageField(upload_to=get_file_path, default=None, blank=True, null=True)

    def __str__(self):
        return str(self.user.username)+" "+str(self.user.first_name)+" "+str(self.user.last_name)


class StudentGroup(models.Model):
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=250)
    desc = models.TextField(blank=True)
    students = models.ManyToManyField(Student)

    def __str__(self):
        return self.name


class Collection(models.Model):
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=250)
    desc = models.TextField(blank=True)
    picture_url = models.URLField(default="http://uupload.ir/files/e799_comb.png")
    students = models.ForeignKey(StudentGroup, blank=True, null=True, on_delete=models.CASCADE)
    #is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class OJHandle(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    judge = models.CharField(max_length=250)
    handle = models.CharField(max_length=250)

    password = models.CharField(max_length=250)


class SupporterTag(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, default=1)


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
    verified = models.BooleanField(default=False)
