from django.contrib import admin
from django.contrib.auth.models import User

from .models import Student, OJHandle, StudentGroup, SupporterTag


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
