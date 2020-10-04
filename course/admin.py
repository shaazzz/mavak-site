import nested_admin
from django.contrib import admin

from .models import Course, Lesson, Tag, CollectionLesson


class CollectionLessonInline(admin.StackedInline):
    model = CollectionLesson


class TagInline(nested_admin.NestedStackedInline):
    model = Tag


class CollectionLessonNestedInline(nested_admin.NestedTabularInline):
    model = CollectionLesson


class LessonInline(nested_admin.NestedStackedInline):
    inlines = [CollectionLessonNestedInline]
    model = Lesson


@admin.register(Course)
class CourseAdmin(nested_admin.NestedModelAdmin):
    list_display = ('link', 'name', 'title')
    list_display_links = ("link",)
    list_editable = ('title', 'name')
    inlines = [
        LessonInline,
        TagInline,
    ]
