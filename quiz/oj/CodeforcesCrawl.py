import json

from quiz.oj.CodeforcesAPI import CodeforcesAPI, get_scores


def judge(secrets, link, total_score):
    secrets = json.loads(secrets)
    cfApi = CodeforcesAPI(secrets)
    result = get_scores(cfApi.get_scoreboard_helper(link), total_score)
    return result


def add_friends(secrets, handles):
    secrets = json.loads(secrets)
    cfApi = CodeforcesAPI(secrets)
    for handle in handles:
        cfApi.add_friend(handle)
