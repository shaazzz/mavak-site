from django.contrib import admin
from .models import Quiz, Question, Secret, Collection, CollectionQuiz

class QuestionInline(admin.StackedInline):
    model = Question

class CollectionQuizInline(admin.StackedInline):
    model = CollectionQuiz

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    inlines = [
        CollectionQuizInline,
    ]

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    inlines = [
        QuestionInline,
    ]

@admin.register(Secret)
class SecretAdmin(admin.ModelAdmin):
    pass
