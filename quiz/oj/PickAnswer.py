from quiz.models import Question, Answer, Secret
from users.models import OJHandle
from .CodeforcesCrawl import judge as judgeCRAWLCF
from .VJudgeAPI import judge as judgeVJ
from .atcoder import judge as judgeAT
from .codeforces import judge as judgeCF
from .GeeksForGeeks import judge as judgeGeeks


def GeeksForGeeks(q: Question):
    if not (q.text.split()[0].upper() == "GEEKSFORGEEKS"):
        return False
    qs = []
    try:
        Answer.objects.filter(question=q).delete()
        problems = q.text.split()[1:]
        handles = [x.handle for x in OJHandle.objects.filter(judge="GEEKSFORGEEKS")]
        data = judgeGeeks(handles, problems, q.mxgrade)
        ignored = []
        evaled = 0
        for x in data:
            try:
                stu = OJHandle.objects.get(judge="GEEKSFORGEEKS", handle=x['handle']).student
                Answer.objects.create(
                    question=q,
                    student=stu,
                    text=".",
                    grade=x['total_points'],
                    grademsg="تصحیح با داوری خارجی"
                )
                evaled += 1
            except Exception as e:
                ignored.append(str(e))
        qs.append({
            "order": q.order,
            "subtyp": "geeksforgeeks",
            "evaled": evaled,
            "ignored": ignored,
        })
    except Exception as e:
        qs.append({
            "order": q.order,
            "subtyp": "geeksforgeeks",
            "error": str(e),
        })
    return qs


def Codeforces(q: Question):
    if not (q.text[:2] == "CF"):
        return False
    qs = []
    try:
        first_line = q.text.split()[0]
        pl = 1
        pr = 1000000
        if len(q.text.split()) > 1:
            pl, pr = [int(x) for x in q.text[len(first_line):].split()]
        secret = Secret.objects.get(key="CF_API").value
        data = judgeCF(secret, first_line[3:], q.mxgrade, pl, pr)
        ignored = []
        evaled = 0
        for x in data:
            try:
                stu = OJHandle.objects.get(judge="CF", handle=x['handle']).student
                Answer.objects.filter(question=q, student=stu).delete()
                Answer.objects.create(
                    question=q,
                    student=stu,
                    text=".",
                    grade=x['total_points'],
                    grademsg="تصحیح با داوری خارجی"
                )
                evaled += 1
            except Exception as e:
                ignored.append(str(e))
        qs.append({
            "order": q.order,
            "subtyp": "کد فرسز",
            "evaled": evaled,
            "ignored": ignored,
        })
    except Exception as e:
        qs.append({
            "order": q.order,
            "subtyp": "کد فرسز",
            "error": str(e),
        })
    return qs


def AtCoder(q: Question):
    if not (q.text[:2] == "AT"):
        return False
    qs = []
    try:
        Answer.objects.filter(question=q).delete()
        problems = q.text.split("\n")[1].split(" ")
        handles = [x.handle for x in OJHandle.objects.filter(judge="ATCODER")]
        data = judgeAT(handles, problems, q.mxgrade)
        ignored = []
        evaled = 0
        for x in data:
            try:
                stu = OJHandle.objects.get(judge="ATCODER", handle=x['handle']).student
                Answer.objects.create(
                    question=q,
                    student=stu,
                    text=".",
                    grade=x['total_points'],
                    grademsg="تصحیح با داوری خارجی"
                )
                evaled += 1
            except Exception as e:
                ignored.append(str(e))
        qs.append({
            "order": q.order,
            "subtyp": "اتکدر",
            "evaled": evaled,
            "ignored": ignored,
        })
    except Exception as e:
        qs.append({
            "order": q.order,
            "subtyp": "اتکدر",
            "error": str(e),
        })
    return qs


def CodeforcesCrawl(q: Question):
    if not (q.text.split()[0] == "CRAWLCF"):
        return False
    qs = []
    try:
        secret = Secret.objects.get(key="CF_LOGIN").value
        mode = "private"
        if len(q.text.split()) > 2:
            mode = q.text.split()[2].lower()
        pl = 1
        pr = 1000000
        if len(q.text.split()) > 4:
            pl, pr = int(q.text.split()[3]), int(q.text.split()[4])
        data = judgeCRAWLCF(secret, q.text.split()[1], q.mxgrade, mode, pl, pr)
        ignored = []
        evaled = 0
        for x in data:
            try:
                stu = OJHandle.objects.get(judge="CF", handle=x['handle']).student
                Answer.objects.filter(question=q, student=stu).delete()
                Answer.objects.create(
                    question=q,
                    student=stu,
                    text=".",
                    grade=x['total_points'],
                    grademsg="تصحیح با داوری خارجی"
                )
                evaled += 1
            except Exception as e:
                ignored.append(str(e))
        qs.append({
            "order": q.order,
            "subtyp": "کد فرسز",
            "evaled": evaled,
            "ignored": ignored,
        })
    except Exception as e:
        qs.append({
            "order": q.order,
            "subtyp": "کدفورسز خزش",
            "error": str(e.args),
        })
    return qs


def VJudge(q: Question):
    if not (q.text.split()[0][0:2] == "VJ"):
        return False
    qs = []
    try:
        pl = 1
        pr = 1000000
        if len(q.text.split()) > 2:
            pl, pr = int(q.text.split()[1]), int(q.text.split()[2])
        data = judgeVJ(q.text.split()[0][3:], q.mxgrade, pl, pr)
        ignored = []
        evaled = 0
        for x in data:
            try:
                stu = OJHandle.objects.get(judge="VJ", handle=x['handle']).student
                Answer.objects.filter(question=q, student=stu).delete()
                Answer.objects.create(
                    question=q,
                    student=stu,
                    text=".",
                    grade=x['total_points'],
                    grademsg="تصحیح با داوری خارجی"
                )
                evaled += 1
            except Exception as e:
                ignored.append(str(e))
        qs.append({
            "order": q.order,
            "subtyp": "ویجاج",
            "evaled": evaled,
            "ignored": ignored,
        })
    except Exception as e:
        qs.append({
            "order": q.order,
            "subtyp": "ویجاج",
            "error": str(e.args),
        })
    return qs


functions = [GeeksForGeeks, Codeforces, CodeforcesCrawl, VJudge, AtCoder]


def pick(q: Question):
    for f in functions:
        response = f(q)
        if response:
            return response
