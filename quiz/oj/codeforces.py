import hashlib
import json
import random
import time
from urllib.parse import urlencode

from .ReqHandler import ReqHandler


def generate_random_number(length=6):
    letters = [chr(ord('0') + x) for x in range(10)]
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


class CodeforcesApi:
    req = ReqHandler()

    def __init__(self, secrets):
        self.keys = json.loads(secrets)

    def request(self, method_name, params):
        params["apiKey"] = self.keys["apiKey"]
        params["time"] = int(time.time())
        params = {k: v for k, v in sorted(params.items(), key=lambda item: (item[0], item[1]))}
        random_string = generate_random_number()
        data = random_string + "/" + method_name + "?" + urlencode(params) + "#" + self.keys["apiSecret"]
        params['apiSig'] = random_string + hashlib.sha512(data.encode('utf-8')).hexdigest()
        result = json.loads(self.req.request("https://codeforces.com/api/" + method_name, parameters=params))
        print(result)
        if result["status"] != "OK":
            raise Exception("return status is not ok")
        return result['result']


def judge(secrets, contestId, total_score, pl=1, pr=100000):
    cfApi = CodeforcesApi(secrets)
    result = cfApi.request("contest.standings",
                           {"contestId": contestId, "showUnofficial": "true"})
    problem_cnt = min(len(result['problems']), pr) - pl + 1
    problem_score = total_score / problem_cnt

    users = []
    for user in result['rows']:
        score = 0
        index = 0
        for problem in user["problemResults"]:
            index += 1
            if pl <= index <= pr:
                score += problem['points']
        users.append({
            'handle': user['party']['members'][0]['handle'].lower(),
            "rank": user['rank'],
            'total_points': score * problem_score,
        })
    return users
