from django.contrib import admin
from .models import Student, OJHandle

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