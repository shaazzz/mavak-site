from django.contrib import admin
from .models import Student, OJHandle, StudentGroup

class OJHandleInline(admin.StackedInline):
    model = OJHandle

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    ordering = ('user__username',)
    list_display = ('user', 'ostan', 'shomare', 'verified')
    list_editable = ( 'verified', )
    inlines = [
        OJHandleInline,
    ]

@admin.register(StudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('students',)