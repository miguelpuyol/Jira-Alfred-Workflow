from lib.jira.resources import Board

__author__ = 'miguelpuyol'
import argparse
import sys

from workflow import Workflow
from lib.jira import JIRA


class JiraWorkflowException(Exception):
    """Raised by JiraWorkflow constructor"""


class JiraWorkflow(object):

    def __init__(self, wf):
        self.wf = wf
        username = self.username()
        keychain = self.keychain()
        server = self.server()
        self.client = None
        if username and keychain and server:
            password = wf.get_password(account=username, service=keychain)
            auth = (username, password)
            self.client = JiraClient(server=server, basic_auth=auth)
        else:
            missing = [x for x in (username, keychain, server) if not x]
            err = JiraWorkflowException('Error connecting to the Jira Server', 'Missing {0}'.format(','.join(missing)))
            err.retcode = 30
            raise err

    def server(self):
        server = self.wf.settings.get('server', None)
        return server

    def keychain(self):
        keychain = self.wf.settings.get('keychain', None)
        return keychain

    def username(self):
        username = self.wf.settings.get('user', None)
        return username

    @staticmethod
    def search_key_for_board(board):
        """Generate a string search key for a story or subtasks"""
        elements = [str(board.id)]
        if board.name:
            elements.append(board.name)
        return u' '.join(elements)

    def list_boards(self, query=None):
        boards = self.wf.cached_data('boards', self.client.list_boards, max_age=60)
        for board in self.wf.filter(query, boards, max_results=7, key=self.search_key_for_board):
            # for board in boards:
            self.wf.add_item(title=board.name, subtitle=u'Board Id: {0}'.format(board.id), valid=True,
                             arg=unicode(board.id))


class JiraClient(JIRA):

    def list_boards(self):
        return [SimpleBoard(b.id, b.name) for b in super(JiraClient, self).boards()]


class SimpleBoard(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
