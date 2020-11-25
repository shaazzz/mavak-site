import json
import re
from datetime import datetime

from background_task import background

from quiz.models import Question, Answer, Secret
from users.models import OJHandle
from .CodeforcesCrawl import judge as judgeCRAWLCF
from .GeeksForGeeks import judge as judgeGeeks
from .VJudgeAPI import judge as judgeVJ
from .atcoder import judge as judgeAT
from .codeforces import judge as judgeCF


class Judge:
    pattern = ""

    def pickAnswer(self, q: Question):
        pass

    def getView(self, q: Question):
        pass


class GeeksForGeeks(Judge):
    pattern = r"GEEKSFORGEEKS[\s\S]*"

    def getView(self, q: Question):
        if not re.match(self.pattern, q.text, re.IGNORECASE):
            return False
        problems = q.text.split()[1:]
        index = 1
        text = '<a href="https://www.geeksforgeeks.org/">ثبت‌نام در سایت GeeksForGeeks</a>'
        text += '<br>پس از ثبت‌نام در سایت، حتما username خود را در ' \
                '<a href="https://mavak.shaazzz.ir/users/handles/">اینجا</a>' \
                ' ثبت کنید'
        text += "<br><br>"
        for problem in problems:
            text += '<li><a href="https://practice.geeksforgeeks.org/problems/{}/0">سوال {}: {}</a></li>'.format(
                problem, index, problem)
            index += 1
        return text

    def pickAnswer(self, q: Question):
        if not re.match(self.pattern, q.text, re.IGNORECASE):
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


class Codeforces(Judge):
    pattern = r"CF[\s\S]*"

    def getView(self, q: Question):
        if not re.match(self.pattern, q.text, re.IGNORECASE):
            return False
        contestId = q.text.split()[0][3:]
        group = Secret.objects.get(key="CF_GROUP").value
        text = '<a href="https://codeforces.com/register">ثبت‌نام در سایت Codeforces</a>'.format(group)
        text += '<br>پس از ثبت‌نام در سایت، حتما username خود را در ' \
                '<a href="https://mavak.shaazzz.ir/users/handles/">اینجا</a>' \
                ' ثبت کنید'
        text += '<br><a href="https://codeforces.com/group/{}/join">ثبت‌نام در گروه Codeforces</a>'.format(group)
        text += '<br><a href="https://codeforces.com/group/{}/contest/{}">لینک Contest</a>'.format(group, contestId)
        return text

    def pickAnswer(self, q: Question):
        if not re.match(self.pattern, q.text, re.IGNORECASE):
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


class AtCoder(Judge):
    pattern = r"AT[\s\S]*"

    def getView(self, q: Question):
        if not re.match(self.pattern, q.text, re.IGNORECASE):
            return False
        problems = q.text.split()[1:]
        index = 1
        text = '<a href="https://atcoder.jp/register">ثبت‌نام در سایت AtCoder</a>'
        text += '<br>در ثبت‌نام، میتوانید قسمت‌هایی که ستاره ندارند را خالی بگذارید'
        text += '<br>پس از ثبت‌نام در سایت، حتما username خود را در ' \
                '<a href="https://mavak.shaazzz.ir/users/handles/">اینجا</a>' \
                ' ثبت کنید'
        text += "<br><br>"
        for problem in problems:
            text += '<li><a href="https://atcoder.jp/contests/{}/tasks/{}">سوال {}: {}</a></li>'.format(
                problem.split('_')[0], problem, index, problem)
            index += 1
        return text

    def pickAnswer(self, q: Question):
        if not re.match(self.pattern, q.text, re.IGNORECASE):
            return False
        qs = []
        try:
            Answer.objects.filter(question=q).delete()
            problems = q.text.split()[1:]
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


class CodeforcesCrawl(Judge):
    pattern = r"CRAWLCF[\s\S]*"

    def getView(self, q: Question):
        if not re.match(self.pattern, q.text, re.IGNORECASE):
            return False
        contestLink = q.text.split()[1]
        group = Secret.objects.get(key="CF_GROUP").value
        text = '<a href="https://codeforces.com/register">ثبت‌نام در سایت Codeforces</a>'.format(group)
        text += '<br>پس از ثبت‌نام در سایت، حتما username خود را در ' \
                '<a href="https://mavak.shaazzz.ir/users/handles/">اینجا</a>' \
                ' ثبت کنید'
        text += '<br><a href="https://codeforces.com/group/{}/join">ثبت‌نام در گروه Codeforces</a>'.format(group)
        text += '<br><a href="https://codeforces.com/{}">لینک Contest</a>'.format(contestLink)
        if len(q.text.split()) > 4:
            pl, pr = int(q.text.split()[3]), int(q.text.split()[4])
            text += '<br> سوالات {} تا {} این کانتست رو بزنید'.format(pl, pr)
        return text

    def pickAnswer(self, q: Question):
        if not re.match(self.pattern, q.text, re.IGNORECASE):
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
                    print(x['handle'])
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
                    print(str(e))
                    ignored.append(str(e))
            qs.append({
                "order": q.order,
                "subtyp": "کد فرسز",
                "evaled": evaled,
                "ignored": ignored,
            })
        except Exception as e:
            print(str(e))
            qs.append({
                "order": q.order,
                "subtyp": "کدفورسز خزش",
                "error": str(e.args),
            })
        return qs


class VJudge(Judge):
    pattern = r"VJ[\s\S]*"

    def getView(self, q: Question):
        if not re.match(self.pattern, q.text, re.IGNORECASE):
            return False
        contestId = q.text.split()[0][3:]
        text = '<a href="https://vjudge.net/">ثبت‌نام در سایت VJudge</a>'
        text += '<br>در ثبت‌نام، میتوانید QQ را خالی بگذارید'
        text += '<br>پس از ثبت‌نام در سایت، حتما username خود را در ' \
                '<a href="https://mavak.shaazzz.ir/users/handles/">اینجا</a>' \
                ' ثبت کنید'
        text += '<br><a href="https://vjudge.net/contest/{}">لینک Contest</a>'.format(contestId)
        return text

    def pickAnswer(self, q: Question):
        if not re.match(self.pattern, q.text, re.IGNORECASE):
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


#@background
def pick(q_id):
    print("Hi")
    q = Question.objects.get(id=q_id)
    for cls in Judge.__subclasses__():
        response = cls().pickAnswer(q)
        if response:
            with open("tasks.log", "a") as f:
                f.write(datetime.now().strftime('%m/%d/%Y') + ":" + str(q.id) + json.dumps(response))
            return response


def getView(q: Question):
    for cls in Judge.__subclasses__():
        response = cls().getView(q)
        if response:
            return response