#!/usr/bin/python
# encoding: utf-8
import argparse
import sys

from workflow import Workflow
from lib.jira import JIRA

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
        wf.add_item(title=u'No sprints found', subtitle=u'try later')


def list_incomplete_stories(query):
    # incompleted_stories = wf.cached_data('stories', get_incompleted_stories, max_age=60)

    incompleted_stories = get_incompleted_stories()
    if not incompleted_stories:
        wf.add_item(title=u'No sprint found!', subtitle=u'Create a new sprint or select another Board')
    else:
        if query:
            incompleted_stories=wf.filter(query, incompleted_stories, key=search_key_for_issue)

        for story in incompleted_stories:
            if story.key:
                log.info(story.key)
                full_story = get_issue(story.key)
                title = ' - '.join([story.key, story.fields.summary])
                subtitle = ' - '.join([story.fields.priority.name, story.fields.status.name])
                wf.add_item(title=title, subtitle=subtitle, arg=story.permalink(),
                            autocomplete='--story ' + story.key + ' ',
                            largetext=full_story.fields.description, copytext=story.key)
                wf.store_data('key', story.key)



def get_sprints(latest_first=True):
    log.info('Retrieving the sprints from JIRA')
    sprints = jira.sprints(board_id)
    sprints = sorted((sprint for sprint in sprints if sprint.name.startswith("Sprint")),
                     key=lambda x: int(x.name.split(' ')[1]), reverse=latest_first)
    return sprints


def get_current_sprint():
    sprints = get_sprints()
    if sprints and len(sprints) > 0:
        return sprints[0]

    return None


def get_incompleted_stories():
    current_sprint = get_current_sprint()
    if current_sprint:
        log.info('Getting the incompleted stories for Sprint: ' + current_sprint.name)
        return [jira.issue(x.key) for x in jira.incompleted_issues(board_id, current_sprint.id)]

    return None


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
            wf.add_item(title=u'Error connecting to the Jira Server', subtitle=u'Please check the connections details')
            wf.send_feedback()
        else:
            wf.add_item(title=u'Please setup a valid Board Id', subtitle='Board Id: ' + board_id + ' is not valid')
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
            wf.add_item(title=title, subtitle=subtitle, arg=subtask.permalink(),
                        largetext=subtask.fields.summary, copytext=subtask.key,
                        autocomplete='--subtask ' + subtask.key)
    else:
        wf.add_item(title=u'The story has no subtasks', subtitle=u'Click to create one (not yet)', valid=False)
    wf.add_item(title=u'Go back', autocomplete='--story ' + story_key)

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
    wf.add_item(title=u'Open in Browser', subtitle=u'opens in your default browser',
                largetext=issue.fields.description,
                copytext=story_key,
                arg=issue.permalink(), valid=True)
    if not is_subtask:
        wf.add_item(title=u'Browse Subtasks', subtitle=u'Show all the tasks of the story',
                    autocomplete='--subtasks ' + story_key + ' ')
    wf.add_item(title='Status: ' + issue.fields.status.name, subtitle=issue.fields.status.description,
                largetext=issue.fields.status.name)
    if issue.fields.assignee:
        wf.add_item(title='Assignee: ' + issue.fields.assignee.displayName, subtitle=issue.fields.assignee.name)

    if issue.fields.comment and issue.fields.comment.total > 0:
        wf.add_item(title=u'Browse comments ', subtitle='Total Comments: ' + str(issue.fields.comment.total),
                    autocomplete='--comments ' + story_key + ' ')
    if not is_subtask:
        wf.add_item(title=u'Go back', autocomplete=u'')
    else:
        wf.add_item(title=u'Go back', autocomplete=u'--subtasks ' + issue.fields.parent.key)


def show_subtask_options(story_key, title):
    wf.add_item(title='Creating Subtask For: ' + story_key, subtitle=title)
    wf.store_data('subtask_title', title)
    wf.add_item(title=u'Save it!', subtitle=title, autocomplete=u'--save')


def create_subtask(parent_key, description):
    log.info(' '.join('Creating subtask', description, u'for story', parent_key))
    parent_story = get_issue(parent_key)
    subtask_fields = {
        'project': {'key': parent_story.fields.project.key},
        'summary': 'Test child auto created issue',
        'description': description,
        'issuetype': {'name': 'Sub-task'},
        'parent': {'id': parent_story.key},
    }

    jira.create_issue(fields=subtask_fields)


def list_story_comments(story_key, is_subtask=False):
    issue = get_issue(story_key)
    for comment in issue.fields.comment.comments:
        wf.add_item(title=comment.body,
                    largetext=comment.body, copytext=comment.body,
                    subtitle=comment.author.name, valid=True, arg=comment.self)

    if is_subtask:
        wf.add_item(title=u'Go back', autocomplete=u'--subtasks ' + story_key)
    else:
        wf.add_item(title=u'Go back', autocomplete=u'--story ' + story_key)

def search_key_for_issue(issue):
    """Generate a string search key for a story or subtasks"""
    elements = []
    elements.append(issue.key)
    if issue.fields.summary:
        elements.append(issue.fields.summary)
    if issue.fields.description:
        elements.append(issue.fields.description)  # description
    return u' '.join(elements)


def list_boards(query=None):
    boards = jira.dashboards(filter=query, startAt=0, maxResults=8)
    for board in boards:
        wf.add_item(title=board.name, subtitle=board.id)
    # wf.add_item(title='More', autocomplete=u'--boards '+ str(initial + 1))

def main(wf):
    log.info(wf.args)

    parser = argparse.ArgumentParser()
    parser.add_argument('--story', dest='story', nargs='?', default=None)
    parser.add_argument('--subtasks', dest='subtasks', nargs='?', default=None)
    parser.add_argument('--subtask', dest='subtask', nargs='?', default=None)
    parser.add_argument('--comments', dest='comments', nargs='?', default=None)
    parser.add_argument('--comments_sub', dest='comments_sub', nargs='?', default=None)
    parser.add_argument('--add_subtasks', dest='add_subtask', nargs='?', default=None)
    parser.add_argument('--boards',  dest='boards', nargs='?', default=None)

    # parser.add_argument('--save', dest='save_subtask', nargs='?', default=None)
    parser.add_argument('query', nargs='?', default=None)

    args = parser.parse_args(wf.args)

    if args.story:
        show_story_options(args.story)

    elif args.subtask:
        show_story_options(args.subtask, is_subtask=True)

    elif args.subtasks:
        list_subtasks(args.subtasks)

    elif args.comments:
        list_story_comments(args.comments)

    elif args.comments_sub:
        list_story_comments(args.comments, is_subtask=True)

    elif args.add_subtask:
        show_subtask_options(args.add_subtask, args.title)

    elif args.boards:
        list_boards("favourite")

    # elif args.save_subtask:
    #     create_subtask(wf.stored_data('key'), wf.stored_data('subtask_title'))

    else:
        list_incomplete_stories(args.query)

    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    # wf.cache_serializer = 'cpickle'
    log = wf.logger
    board_id = wf.settings.get('sprint_board', None)
    jira = setup()
    sys.exit(wf.run(main))
