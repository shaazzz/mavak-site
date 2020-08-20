from django.contrib import admin
from .models import Quiz, Question, Secret

class QuestionInline(admin.StackedInline):
    model = Question

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    inlines = [
        QuestionInline,
    ]

@admin.register(Secret)
class SecretAdmin(admin.ModelAdmin):
    pass
