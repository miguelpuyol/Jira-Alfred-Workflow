import pytest
from workflow import Workflow
from JiraWorkflow import JiraWorkflow


@pytest.fixture(scope="class")
def jira():
    wf = Workflow()
    jira = JiraWorkflow(wf)
    return jira

def test_jira(jira):
    # result = jira.jira.boards()
    result = jira.jira.list_boards()
    assert result is not None
    # assert not result.exception
    # assert result.output.strip() == 'Setting password for Pubsub on stage.'
    # result = cf.__read_password('stage')
    # assert  result == '@$123'
#
# def test_cli_with_option(runner):
#     result = runner.invoke(cli.main, ['--as-cowboy'])
#     assert not result.exception
#     assert result.exit_code == 0
#     assert result.output.strip() == 'Howdy, world.'
#
#
# def test_cli_with_arg(runner):
#     result = runner.invoke(cli.main, ['Miguel'])
#     assert result.exit_code == 0
#     assert not result.exception
#     assert result.output.strip() == 'Hello, Miguel.'
