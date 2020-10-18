from django import forms
from django.contrib import admin
from searchableselect.widgets import SearchableSelect

from .models import Quiz, Question, Secret, CollectionQuiz, Answer, RateColor, Tag


class QuestionInline(admin.StackedInline):
    model = Question


class CollectionQuizForm(forms.ModelForm):
    class Meta:
        model = CollectionQuiz
        exclude = ()
        widgets = {
            "quiz": SearchableSelect(many=False, model='quiz.quiz', search_field='title', limit=10),
        }


class CollectionQuizInline(admin.StackedInline):
    model = CollectionQuiz
    form = CollectionQuizForm


class TagInline(admin.StackedInline):
    model = Tag


class QuizInline(admin.StackedInline):
    model = Quiz


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('link', 'name', 'title')
    list_display_links = ("link",)
    list_editable = ('title', 'name')
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
    ordering = ('question',)
    list_display = ('question', 'student', 'text', 'grade', 'grademsg')
    list_editable = ('grade', 'grademsg')


@admin.register(RateColor)
class RateAdmin(admin.ModelAdmin):
    pass
