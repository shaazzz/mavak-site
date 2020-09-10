from django.contrib import admin

# Register your models here.
from comment.models import Comment
from main.models import Tag


@admin.register(Tag)
class AdminTag(admin.ModelAdmin):
    pass
