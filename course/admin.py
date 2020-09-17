import nested_admin
from django.contrib import admin

from .models import Course, Lesson, Tag, CollectionLesson


class TagInline(nested_admin.NestedStackedInline):
    model = Tag


class CollectionLessonInline(nested_admin.NestedTabularInline):
    model = CollectionLesson


class LessonInline(nested_admin.NestedStackedInline):
    inlines = [CollectionLessonInline]
    model = Lesson


@admin.register(Course)
class CourseAdmin(nested_admin.NestedModelAdmin):
    inlines = [
        LessonInline,
        TagInline,
    ]

#admin.site.register(CourseAdmin, CourseAdmin)