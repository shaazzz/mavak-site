import nested_admin
from django import forms
from django.contrib import admin
from jalali_date.admin import StackedInlineJalaliMixin
from jalali_date.widgets import AdminSplitJalaliDateTime
from searchableselect.widgets import SearchableSelect

from .models import Course, Lesson, Tag, CollectionLesson


class CollectionLessonForm(forms.ModelForm):
    class Meta:
        model = CollectionLesson
        exclude = ()
        widgets = {
            "lesson": SearchableSelect(many=False, model='course.Lesson', search_field='title', limit=10),
            "start": AdminSplitJalaliDateTime(),
            "end": AdminSplitJalaliDateTime()
        }


class CollectionLessonInline(StackedInlineJalaliMixin, admin.StackedInline):
    model = CollectionLesson
    form = CollectionLessonForm


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
