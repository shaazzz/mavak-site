from django.contrib import admin
from .models import Quiz, Question, Secret, Collection, CollectionQuiz, Answer, RateColor, Tag


class QuestionInline(admin.StackedInline):
    model = Question


class CollectionQuizInline(admin.StackedInline):
    model = CollectionQuiz


class TagInline(admin.StackedInline):
    model = Tag


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    inlines = [
        CollectionQuizInline,
    ]


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    inlines = [
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
