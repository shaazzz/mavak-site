import urllib.parse
import urllib.request
from os import system, name

def judge(users, problem_ids, total_score):

    problem_score = total_score / len(problem_ids)
    output = []

    total_pages = len(problem_ids) * len(users)
    page_id = 0

    for user in users:
        sum_score = 0
        for problem_id in problem_ids:
            page_id += 1
            contest_id = problem_id.split('_')[0]
            url = 'https://atcoder.jp/contests/' + contest_id + '/submissions?f.Task=' + problem_id + '&f.Language=&f.Status=AC&f.User=' + user
            response = urllib.request.urlopen(url)
            webContent = response.read()
            result = webContent.decode("utf-8").find('class="text-right submission-score"')
            if result != -1:
                sum_score += problem_score
        output.append({
            "handle": user,
            "total_points": sum_score
        })
    return output
