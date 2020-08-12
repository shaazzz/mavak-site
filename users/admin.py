from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
  list_display = ('user', 'ostan', 'shomare', 'verified')
  list_editable = ( 'verified', )