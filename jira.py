#!/usr/bin/python
# encoding: utf-8


import sys

from workflow import Workflow
from jira import JIRA

log = None
jira = None
board_id = None


def list_sprints(wf):
    sprints = wf.cached_data('sprints', get_sprints, max_age=360)

    if sprints:
        for sprint in sprints:
            log.info("Sprint: %s" % sprint.name)
            log.info("Sprint Id: %s" % sprint.id)
            wf.add_item(title=sprint.name, valid=True)
    else:
        wf.add_item(title='No sprints found', subtitle='try later')


def list_incomplete_stories(wf):
    # incompleted_stories = wf.cached_data('incompleted_stories', get_incompleted_stories, max_age=60)
    #
    incompleted_stories = get_incompleted_stories()
    for story in incompleted_stories:
        if story.key:
            log.info(story.key)
            title = ' - '.join([story.key, story.summary])
            subtitle = ' - '.join([story.priorityName, story.status.name])
            wf.add_item(title=title, subtitle=subtitle, arg=story.permalink(), valid=True)



def get_sprints(latest_first=True):
    log.info('Retrieving the sprints from JIRA')
    sprints = jira.sprints(board_id)
    sprints = sorted((sprint for sprint in sprints if sprint.name.startswith("Sprint")),
                     key=lambda x: int(x.name.split(' ')[1]), reverse=latest_first)
    return sprints


def get_current_sprint():
    return get_sprints()[0]


def get_incompleted_stories():
    current_sprint = get_current_sprint()
    log.info('Getting the incompleted stories for Sprint: ' + current_sprint.name)
    return jira.incompleted_issues(board_id, current_sprint.id)



def setup(wf):
    username = wf.settings.get('user', None)
    keychain = wf.settings.get('keychain', None)
    server = wf.settings.get('server', None)

    if username and keychain and server and board_id:
        password = wf.get_password(account=username, service=keychain)
        auth = (username, password)
        return JIRA(server=server, basic_auth=auth)
    else:
        if board_id and int(board_id):
            wf.add_item(title='Error connecting to the Jira Server', subtitle='Please check the connections details')
            wf.send_feedback()
        else:
            wf.add_item(title='Please setup a valid Board Id', subtitle='Board Id: ' + board_id + ' is not valid')
            wf.send_feedback()
    return None

def main(wf):
    log.info(wf.args)
    # wf.add_item(title='Loading Sprints', subtitle='test')
    # wf.send_feedback()
    # list_sprints(wf)
    list_incomplete_stories(wf)
    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    board_id = wf.settings.get('sprint_board', None)
    jira = setup(wf)
    sys.exit(wf.run(main))
