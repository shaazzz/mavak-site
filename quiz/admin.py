from django.contrib import admin
from .models import Quiz, Question, Secret, CollectionQuiz, Answer, RateColor, Tag


class QuestionInline(admin.StackedInline):
    model = Question


class CollectionQuizInline(admin.StackedInline):
    model = CollectionQuiz


class TagInline(admin.StackedInline):
    model = Tag


class QuizInline(admin.StackedInline):
    model = Quiz


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    inlines = [
        CollectionQuizInline,
        QuestionInline,
        TagInline,
    ]


@admin.register(Secret)
class SecretAdmin(admin.ModelAdmin):
    pass


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    pass


@admin.register(RateColor)
class RateAdmin(admin.ModelAdmin):
    pass
