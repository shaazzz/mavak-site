from django.contrib import admin

from .models import Course, Lesson, Tag


class LessonInline(admin.StackedInline):
    model = Lesson


class TagInline(admin.StackedInline):
    model = Tag


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [
        LessonInline,
        TagInline,
    ]
