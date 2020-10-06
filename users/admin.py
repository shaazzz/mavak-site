from django.contrib import admin

from course.admin import CollectionLessonInline
from quiz.admin import CollectionQuizInline
from .models import Student, OJHandle, StudentGroup, SupporterTag, Collection


class OJHandleInline(admin.StackedInline):
    model = OJHandle


class SupporterTagInline(admin.StackedInline):
    model = SupporterTag


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    ordering = ('user__username',)
    list_display = ('user', 'ostan', 'shomare', 'verified')
    list_editable = ('verified',)
    inlines = [
        OJHandleInline,
        SupporterTagInline,
    ]


@admin.register(StudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('students',)


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'desc', 'picture_url', 'students')
    list_editable = ('title', 'desc', 'picture_url', 'students')
    inlines = [
        CollectionQuizInline, CollectionLessonInline,
    ]
