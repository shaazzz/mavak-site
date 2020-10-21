import json
import random
import re
from datetime import datetime

import lxml.html as LH

from quiz.oj.RequestHandler import RequestHandler


def generate_random_string(length=6):
    letters = "abcdefghijklmnopqrstuvwxyz0123456789"
    result_str = ''.join(random.choice(letters) for _ in range(length))
    return result_str


def text(elt):
    return elt.text_content().replace(u'\xa0', u' ').strip()


def check_login_helper(body):
    if re.search(r"handle = \"([\s\S]+?)\"", body):
        return True
    return False


def get_value_from_body(body, name):
    x = re.search(r"name=\"" + name + r"\" value=\"([\s\S]+?)\"", body)
    if x is None:
        raise Exception("can't find ", name, body)
    return x.group(1)


def get_placeholder_from_body(body, name):
    x = re.search(r"name=\"" + name + r"\" value=\"\" placeholder=\"([\s\S]+?)\"", body)
    if x is None:
        raise Exception("can't find ", name, body)
    return x.group(1)


def get_scores(scoreboard, total_score, pl=1, pr=100000):
    users = []
    index = 0
    for user in scoreboard:
        index += 1
        points = 0
        ind_col = 1
        for col in scoreboard[user]:
            if pl <= ind_col <= pr and scoreboard[user][col]:
                points += 1
            ind_col += 1

        problem_cnt = min(len(scoreboard[user]), pr) - pl + 1
        users.append({
            'handle': user.lower(),
            "rank": index,
            'total_points': total_score * points / problem_cnt,
        })
    return users


class CodeforcesAPI:
    url = 'https://codeforces.com/'
    req = RequestHandler()
    csrf_token = None
    ftaaCode = generate_random_string(18)
    bfaaCode = "d832303e1034c022d32d78576e5c24f5"

    def __init__(self, secrets):
        self.find_csrf()
        self.login(secrets["codeforces_username"], secrets["codeforces_password"])

    def find_csrf(self):
        body = self.req.request(self.url, req_type="get")
        x = re.search(r"csrf='(.+)'", body)
        if x is None:
            raise Exception("cf token not found", body)
        self.csrf_token = x.group(1)

    def checkLogin(self):
        body = self.req.request(self.url, req_type="get")
        return check_login_helper(body)

    def getAdditionalParameters(self):
        return {
            "csrf_token": self.csrf_token,
            "ftaa": self.ftaaCode,
            "bfaa": self.bfaaCode,
            "_tta": "428"
        }

    def request(self, action_address, parameters, return_everything=False, add_additional_parameters=True):
        if add_additional_parameters:
            parameters = dict(parameters, **self.getAdditionalParameters())
        body = self.req.request(self.url + action_address, parameters)
        return body

    def login(self, username, password):
        result = self.request('enter', {
            "action": "enter",
            "handleOrEmail": username,
            "password": password,
            "remember": "on"
        })
        if check_login_helper(result):
            print("login successful")
        else:
            raise Exception("login failed")
        self.find_csrf()

    def get_problem_array_data(self, problem_id):
        result = self.request('data/mashup', {
            "action": "getProblem",
            "problemQuery": problem_id,
            "problemCount": 0
        })
        return json.loads(result)

    def change_time_to_today(self, contest):
        # duration = 15 * 60
        duration = 24 * 60 * 7
        self.request("gym/edit/" + contest.contestId + "?csrf_token=" + self.csrf_token, {
            "csrf_token": self.csrf_token,
            "contestEditFormSubmitted": "true",
            "clientTimezoneOffset": "270",
            "englishName": contest.get_name(),
            "russianName": contest.get_name(),
            "untaggedContestType": "ICPC",
            "initialDatetime": "",
            "startDay": datetime.today().strftime('%Y-%m-%d'),
            "startTime": "00:00",
            "duration": duration,
            "visibility": "PRIVATE",
            "participationType": "PERSONS_ONLY",
            "freezeDuration": "0",
            "initialUnfreezeTime": "",
            "unfreezeDay": "",
            "unfreezeTime": "",
            "allowedPractice": "on",
            "allowedSelfRegistration": "on",
            "allowedViewForNonRegistered": "on",
            "allowedCommonStatus": "on",
            "viewTestdataPolicy": "OWN_FAILED",
            "submitViewPolicy": "NONE",
            "languages": "true",
            "allowedStatements": "on",
            "allowedStandings": "on",
            "season": "",
            "contestType": "",
            "icpcRegion": "",
            "country": "",
            "city": "",
            "difficulty": "0",
            "websiteUrl": "http://mavak.shaazzz.ir",
            "englishDescription": "",
            "russianDescription": "",
            "englishRegistrationConfirmation": "",
            "russianRegistrationConfirmation": "",
            "_tta": "428"
        }, False, False)

    '''
    # naghes
    def get_participates(self, contest_id):
        result = self.request('gymRegistrants/' + str(contest_id), {})
        tree = html.fromstring(result)
        class_name = "registrants"
        nodes = tree.xpath("//*[contains(concat(' ', normalize-space(@class), ' '), ' " + class_name + " ')]")
        print(nodes)
        $table_doc = new
        DOMDocument();
        $cloned = $nodes[0]->cloneNode(TRUE);
        $table_doc->appendChild($table_doc->importNode($cloned, True));
        $finder = new
        DOMXPath($table_doc);

        $classname = "rated-user";
        users = $finder->query("//*[contains(concat(' ', normalize-space(@class), ' '), ' $classname ')]");
        users_id = array();
        for (user_id in users) {
            users_id.append(trim(user_id->nodeValue));
        }
        return users_id
    '''

    def get_scoreboard_helper(self, link, mode="private"):
        page = 0
        scoreboard = {}
        rnk = 0
        while True:
            page += 1
            clink = link + "/page/" + str(page) + "/"
            if mode == "edu":
                clink = link + "?page=" + str(page) + "&friends=true"
            result = self.request(clink, {})
            root = LH.fromstring(result)
            class_name = "standings"
            table = root.xpath("//table[contains(concat(' ', normalize-space(@class), ' '), ' " + class_name + " ')]")[
                0]
            header = [text(th) for th in table.xpath('//th')]  # 1
            data = [[{"att": td.attrib, "text": text(td)} for td in tr.xpath('td')]
                    for tr in table.xpath('//tr')]  # 2

            for participant in data:
                if len(participant) < 2:
                    continue
                user_id = participant[1]['text'].replace("*", "").strip()
                rank = participant[0]['text'].strip()
                if not user_id.startswith("Accepted"):
                    rnk += 1
                    if user_id in scoreboard:
                        return scoreboard
                else:
                    break
                scoreboard[user_id] = {}
                index = 0
                for column in participant:
                    if "problemid" in column["att"]:
                        if index in scoreboard[user_id]:
                            scoreboard[user_id][index] |= "acceptedsubmissionid" in column["att"]
                        else:
                            scoreboard[user_id][index] = "acceptedsubmissionid" in column["att"]
                        index += 1

    def get_scoreboard(self, contest_id, contest_address_prefix="gym", contest_address_suffix=""):
        return self.get_scoreboard_helper(contest_address_prefix + '/' + str(contest_id)
                                          + "/standings/" + contest_address_suffix)

    def add_friend(self, handle):
        body = self.req.request(self.url + "profile/" + handle, req_type="get")
        x = re.search(r'friendUserId="(.+?)"', body)
        if x is None:
            raise Exception("friendUserId not found", body)
        user_id = x.group(1)
        result = self.request("data/friend", {
            "friendUserId": user_id,
            "isAdd": "true"
        })
        if result != "{\"success\":\"true\"}":
            raise Exception("can't add friend ", handle)
        print(handle, user_id, "added to admin friends")
