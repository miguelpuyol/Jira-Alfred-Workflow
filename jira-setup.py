#!/usr/bin/python
# encoding: utf-8

import sys
import argparse

from workflow import Workflow
from lib.jira import JIRA

log = None
jira = None


def setup(wf):
    username = get_username(wf)
    keychain = get_keychain(wf)
    server = get_server(wf)
    if username and keychain and server:
        password = wf.get_password(account=username, service=keychain)
        auth = (username, password)
        return JIRA(server=server, basic_auth=auth)
    return None


def get_server(wf):
    server = wf.settings.get('server', None)
    return server


def get_keychain(wf):
    keychain = wf.settings.get('keychain', None)
    return keychain


def get_username(wf):
    username = wf.settings.get('user', None)
    return username


def main(wf):
    log.info(wf.args)
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', dest='server', nargs='?', default=None)
    parser.add_argument('--user', dest='user', nargs='?', default=None)
    parser.add_argument('--password', dest='password', nargs='?', default=None)
    parser.add_argument('--setup', dest='setup', nargs='?', default=None)
    parser.add_argument('--sprint_board', dest='sprint_board', nargs='?', default=None)
    # parser.add_argument('--test', dest='test', nargs='?', default=None)
    parser.add_argument('test', nargs='?', default=None)
    # parser.add_argument('server-url', nargs='?', default=None)

    args = parser.parse_args(wf.args)

    if args.server and 'http://' in args.server:
        log.info('Saving new server: ' + args.server)
        wf.settings['server'] = args.server
        return 0

    if args.user:
        log.info('Saving new user: ' + args.user)
        wf.settings['user'] = args.user
        return 0

    if args.password:
        username = wf.settings.get('user', None)
        if username:
            log.info('Setting the password')
            service = 'jira@alfred'
            wf.settings['keychain'] = service
            wf.save_password(username, args.password, service)
            return 0
        else:
            log.error('Error: User not set. The password was not stored')

    if args.sprint_board:
        log.info('Setting the sprint board id')
        wf.settings['sprint_board'] = args.sprint_board
        return 0

    if args.setup:

        if args.test:
            log.info('Testing connection')
            log.info(wf.settings)
            jira = setup(wf)
            if jira:
                log.info(jira)
                wf.add_item(title='Connected to: ' + jira.client_info())
            else:
                wf.add_item(title='Something went wrong!', subtitle='Check the configuration')

        log.info('Displaying config data')
        log.info(wf.settings)
        username = get_username(wf)
        keychain = get_keychain(wf)
        server = get_server(wf)
        sprint_board = wf.settings.get('sprint_board', None)

        if not args.test and username and server and keychain:
            wf.add_item(title='Test the connection', subtitle='Hit enter to test it', autocomplete='test')

        if username:
            wf.add_item(title='Username: ' + username)
        # else:
        #     wf.add_item(title='No username defined', subtitle='Press enter to setup one', autocomplete='--user')

        if server:
            wf.add_item(title='Server: ' + server)
        # else:
        #     wf.add_item(title='No server defined', subtitle='Press enter to setup one', autocomplete='--server')

        if sprint_board:
            wf.add_item(title='Sprint Board Id: ' + sprint_board)

        wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    # jira = setup(wf)
    sys.exit(wf.run(main))
