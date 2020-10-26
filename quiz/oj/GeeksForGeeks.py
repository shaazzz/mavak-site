import lxml.html as LH
import requests


def text(elt):
    return elt.text_content().replace(u'\xa0', u' ').strip()


def get_problems(user):
    link = "https://auth.geeksforgeeks.org/user/{}/practice/".format(user)
    string = requests.get(link).text
    root = LH.fromstring(string)
    problems = [td.attrib['href'].split("/")[-2] for td in root.xpath("//a") if
                'href' in td.attrib and td.attrib['href'].startswith(
                    "https://practice.geeksforgeeks.org/problems/")]
    return problems


def judge(users, problem_ids, total_score):
    problem_score = total_score / len(problem_ids)
    output = []
    for user in users:
        problems = set(get_problems(user)).intersection(problem_ids)
        output.append({
            "handle": user,
            "total_points": len(problems) * problem_score
        })
    return output
