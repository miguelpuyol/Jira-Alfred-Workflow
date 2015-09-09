#!/usr/bin/python
# encoding: utf-8
import argparse

import sys

from workflow import Workflow
from jira import JIRA

log = None
jira = None
board_id = None
wf = None


def list_sprints():
    sprints = wf.cached_data('sprints', get_sprints, max_age=360)

    if sprints:
        for sprint in sprints:
            log.info("Sprint: %s" % sprint.name)
            log.info("Sprint Id: %s" % sprint.id)
            wf.add_item(title=sprint.name, valid=True)
    else:
        wf.add_item(title='No sprints found', subtitle='try later')


def list_incomplete_stories():
    # incompleted_stories = wf.cached_data('stories', get_incompleted_stories, max_age=60)
    #
    incompleted_stories = get_incompleted_stories()
    for story in incompleted_stories:
        if story.key:
            log.info(story.key)
            title = ' - '.join([story.key, story.summary])
            subtitle = ' - '.join([story.priorityName, story.status.name])
            wf.add_item(title=title, subtitle=subtitle, arg=story.permalink(), autocomplete='--story ' + story.key)
            wf.store_data('key', story.key)



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



def setup():
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


def list_subtasks(story_key):
    issue = get_issue(story_key)
    subtasks = issue.fields.subtasks
    # wf.add_item(title='Create a new subtask', autocomplete='--add_subtask ' + story_key)
    if subtasks:
        for subtask in subtasks:
            title = ' - '.join([subtask.key, subtask.fields.summary])
            subtitle = ' - '.join([subtask.fields.priority.name, subtask.fields.status.name])
            wf.add_item(title=title, subtitle=subtitle, arg=subtask.permalink(), autocomplete='--subtask ' + subtask.key)
    else:
        wf.add_item(title='The story has no subtasks', subtitle='Click to create one (not yet)', valid=False)
    wf.add_item(title='Go back', autocomplete='--story ' + story_key)

def _load_issue():
    story_key = wf.cached_data('story-key')
    return jira.issue(story_key)


def get_issue(story_key):
    wf.cache_data('story-key', story_key)
    # story = wf.cached_data('story', _load_issue, max_age=30)
    # return story
    return _load_issue()

def show_story_options(story_key, is_subtask=False):
    issue = get_issue(story_key)
    wf.add_item(title='Open in Browser', subtitle='opens in your default browser', arg=issue.permalink(), valid=True)
    if not is_subtask:
        wf.add_item(title='Browse Subtasks', subtitle='Show all the tasks of the story', autocomplete='--subtasks ' + story_key + ' ')
    wf.add_item(title='Status: ' + issue.fields.status.name, subtitle=issue.fields.status.description)
    if issue.fields.assignee:
        wf.add_item(title='Assignee: ' + issue.fields.assignee.displayName, subtitle=issue.fields.assignee.name)
    wf.add_item(title='Reporter: ' + issue.fields.creator.displayName, subtitle=issue.fields.creator.name)
    # TODO: Show comments option
    if not is_subtask:
        wf.add_item(title='Go back', autocomplete='')
    else:
        wf.add_item(title='Go back', autocomplete='--subtasks ' + issue.parent.key)


def show_subtask_options(story_key, title):
    wf.add_item(title='Creating Subtask For: ' + story_key, subtitle=title)
    wf.store_data('subtask_title', title)
    wf.add_item(title='Save it!', subtitle=title, autocomplete='--save')


def create_subtask(parent_key, description):
    log.info(' '.join('Creating subtask', description, 'for story', parent_key))
    parent_story = get_issue(parent_key)
    subtask_fields = {
        'project' : { 'key': parent_story.fields.project.key },
        'summary' : 'Test child auto created issue',
        'description' : description,
        'issuetype' : { 'name' : 'Sub-task' },
        'parent' : { 'id' : parent_story.key},
    }

    jira.create_issue(fields=subtask_fields)

def main(wf):
    log.info(wf.args)
    # wf.add_item(title='Loading Sprints', subtitle='test')
    # wf.send_feedback()
    # list_sprints(wf)
    # log.info(wf.args)
    parser = argparse.ArgumentParser()
    parser.add_argument('--story', dest='story', nargs='?', default=None)
    parser.add_argument('--subtasks', dest='subtasks', nargs='?', default=None)
    parser.add_argument('--subtask', dest='subtask', nargs='?', default=None)
    parser.add_argument('--add_subtasks', dest='add_subtask', nargs='?', default=None)
    # parser.add_argument('--save', dest='save_subtask', nargs='?', default=None)
    parser.add_argument('title', nargs='?', default=None)

    args = parser.parse_args(wf.args)

    if args.story:
        show_story_options(args.story)

    elif args.subtask:
        show_story_options(args.subtask, is_subtask=True)

    elif args.subtasks:
        list_subtasks(args.subtasks)

    elif args.add_subtask:
        show_subtask_options(args.add_subtask, args.title)

    # elif args.save_subtask:
    #     create_subtask(wf.stored_data('key'), wf.stored_data('subtask_title'))

    else:
        list_incomplete_stories()

    wf.send_feedback()

if __name__ == '__main__':
    wf = Workflow()
    wf.data_serializer = 'json'
    log = wf.logger
    board_id = wf.settings.get('sprint_board', None)
    jira = setup()
    sys.exit(wf.run(main))
