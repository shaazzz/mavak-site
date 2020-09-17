from django.contrib import admin

# Register your models here.
from comment.models import Comment
from main.models import Tag
from course.models import Tag as course_tag
from quiz.models import Tag as quiz_tag


class CourseTagInline(admin.StackedInline):
    model = course_tag


class QuizTagInline(admin.StackedInline):
    model = quiz_tag


@admin.register(Tag)
class AdminTag(admin.ModelAdmin):
    inlines = [
        CourseTagInline,
        QuizTagInline
    ]
