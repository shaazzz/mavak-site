import json

from background_task import background

from quiz.oj.CodeforcesAPI import CodeforcesAPI, get_scores


def judge(secrets, link, total_score, mode="private", pl=1, pr=100000):
    secrets = json.loads(secrets)
    cfApi = CodeforcesAPI(secrets)
    result = get_scores(cfApi.get_scoreboard_helper(link, mode), total_score, pl, pr)
    return result


@background
def add_friends(secrets, handles):
    secrets = json.loads(secrets)
    cfApi = CodeforcesAPI(secrets)
    for handle in handles:
        cfApi.add_friend(handle)
