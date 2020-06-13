from django.contrib import admin
from .models import Course, Lesson

class LessonInline(admin.StackedInline):
    model = Lesson

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [
        LessonInline,
    ]
