from slacker import Slacker
from apscheduler.schedulers.blocking import BlockingScheduler
import github3
import datetime
import pytz
import os

sched = BlockingScheduler()
local_tz = pytz.timezone('Asia/Seoul')
slack_token = os.environ['SLACK_TOKEN']
gh_token = os.environ['GITHUB_ACCESS_TOKEN']

slack = Slacker(slack_token)
channels = ['#_general', '#announcements', '#test_bot']

def post_to_channel(message, idx):
    slack.chat.post_message(channels[idx], message, as_user=True)

def get_repo_last_commit_delta_time(owner, repo_name):
    repo = github3.repository(owner, repo_name)
    return repo.pushed_at.astimezone(local_tz)

def get_delta_time(last_commit):
    now = datetime.datetime.now(local_tz)
    delta = now - last_commit
    return delta.days


# uncomment when testing
# @sched.scheduled_job('interval', seconds=3)
@sched.scheduled_job('cron', day_of_week='mon-sun', hour=14)
def main():
    gh = github3.login(token=gh_token)
    tml = gh.organization(login='ajoutml')
    reports = []

    for member in tml.iter_members():
        owner = member.login
        last_commit = get_repo_last_commit_delta_time(owner, 'TMLgorithm')
        delta_time = get_delta_time(last_commit)

        if(delta_time == 0):
            reports.append('*%s* 님은 오늘 커밋을 하셨어요!'
                           % (owner))
        else:
            reports.append('*%s* 님은 *%s* 일이나 커밋을 안하셨어요!'
                           % (owner, delta_time))

    post_to_channel('\n 안녕 친구들! 과제 점검하는 커밋벨이야 호호 \n'
                    + '\n'.join(reports), 0)

if __name__ == '__main__':
    sched.start()
