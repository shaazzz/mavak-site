import nested_admin
from django import forms
from django.contrib import admin
from jalali_date.fields import SplitJalaliDateTimeField, JalaliDateField
from jalali_date.widgets import AdminSplitJalaliDateTime, AdminJalaliDateWidget
from searchableselect.widgets import SearchableSelect

from .models import Course, Lesson, Tag, CollectionLesson


class CollectionLessonForm(forms.ModelForm):
    class Meta:
        model = CollectionLesson
        exclude = ()
        widgets = {
            "lesson": SearchableSelect(many=False, model='course.Lesson', search_field='title', limit=10),
        }

    def __init__(self, *args, **kwargs):
        super(CollectionLessonForm, self).__init__(*args, **kwargs)
        self.fields['start'] = SplitJalaliDateTimeField(
            widget=AdminSplitJalaliDateTime
            # required, for decompress DatetimeField to JalaliDateField and JalaliTimeField
        )
        self.fields['date'] = JalaliDateField(  # date format is  "yyyy-mm-dd"
            widget=AdminJalaliDateWidget  # optional, to use default datepicker
        )
        self.fields['date_time'] = SplitJalaliDateTimeField(
            widget=AdminSplitJalaliDateTime
            # required, for decompress DatetimeField to JalaliDateField and JalaliTimeField
        )


class CollectionLessonInline(admin.StackedInline):
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
