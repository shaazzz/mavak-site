import json

from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import redirect, get_object_or_404, render

from quiz.models import Question, Quiz
from quiz.oj.OJHandler import autoPicker


def index(req):
    return redirect("/users/me")


def update_oj(req):
    if not req.user.is_staff:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    autoPicker()
    return JsonResponse({"ok": True})


def get_model(req):
    if req.GET['type'] == "quiz":
        q = get_object_or_404(Quiz, id=req.GET['id'])
    if req.GET['type'] == "question":
        q = get_object_or_404(Question, id=req.GET['id'])
    return JsonResponse(model_to_dict(q))


def add_model_rec(json_input: object, **kwargs):
    if isinstance(json_input, list):
        for x in json_input:
            add_model_rec(x, **kwargs)
        return
    assert "type" in json_input
    assert "fields" in json_input
    print({**json_input["fields"], **kwargs})
    if json_input["type"] == "quiz":
        kwargs["quiz"] = Quiz.objects.create(**{**json_input["fields"], **kwargs})
    elif json_input["type"] == "question":
        kwargs["question"] = Question.objects.create(**{**json_input["fields"], **kwargs})
    else:
        raise Exception("invalid json input type")
    print(kwargs[json_input["type"]])
    if "children" in json_input:
        add_model_rec(json_input["children"], **kwargs)
    return kwargs[json_input["type"]].id


def add_model(req):
    if not req.user.is_staff:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    if req.method == 'GET':
        return render(req, 'main/add_model.html')
    json_input = json.loads(req.POST['json'])

    if isinstance(json_input, list):
        add_model_rec(json_input)
        return JsonResponse({"ok": True})
    return redirect("/get_model?type={}&id={}".format(str(json_input['type']), str(add_model_rec(json_input))))


'''
t = get_object_or_404(Text, name='home')
return render(req, "main/index.html", {
    'content': markdown(t.text),
})
'''
