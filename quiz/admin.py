from django.contrib import admin
from .models import Quiz, Question

class QuestionInline(admin.StackedInline):
    model = Question

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    inlines = [
        QuestionInline,
    ]
