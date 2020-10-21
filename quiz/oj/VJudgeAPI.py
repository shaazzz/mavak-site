import json
import urllib.parse
import urllib.request

import lxml.html as LH


def judge(contest_id, total_score, pl=1, pr=1000000):
    clink = 'https://vjudge.net/contest/rank/single/' + str(contest_id) + '/'
    link = 'https://vjudge.net/contest/' + str(contest_id) + '/'
    result = urllib.request.urlopen(link).read()
    root = LH.fromstring(result)
    ul_id = "problem-nav"
    ul = root.xpath("//ul[contains(concat(' ', normalize-space(@id), ' '), ' " + ul_id + " ')]")[
        0]
    problem_cnt = len([td.attrib for td in ul.xpath('li')])

    problem_cnt = min(problem_cnt, pr) - pl + 1

    problem_score = total_score / problem_cnt
    ids = {}
    users = []
    result = json.loads(urllib.request.urlopen(clink).read())
    for key, user in result['participants'].items():
        ids[int(key)] = user[0]
    scoreboard = {}
    for row in result['submissions']:
        if ids[row[0]] not in scoreboard:
            scoreboard[ids[row[0]]] = []
        if pl <= row[1] <= pr:
            if row[2] == 1 and row[1] not in scoreboard[ids[row[0]]]:
                scoreboard[ids[row[0]]].append(row[1])
    for user, problems in scoreboard.items():
        users.append({
            'handle': user.lower(),
            'total_points': len(problems) * problem_score,
        })
    return users
