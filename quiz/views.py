from django.shortcuts import render, get_object_or_404
from .models import Quiz
from django.utils import timezone

def quizView(req, name):
    q = get_object_or_404(Quiz, name= name)
    if q.start > timezone.now():
        return render(req, "quiz/not_started.html", {
            'quiz': q,
            'current': timezone.now(),
        })
    return render(req, "quiz/finished.html", {
        'quiz': q,
    }) 
