# Jira Workflow for Alfred

# Prerequisites

Install jira-python package

```
$ pip install jira
```

# Download

Download the workflow file [Jira Task Manager](Jira%20Task%20Manager.alfredworkflow)

# Usage

Type `jira` on Alfred to list the 

# Setup

| Command | Description |
| ------- | ------------|
| `jira`                 | Show the Jira options |
| `setupjiraserver`      | Set the jira server            |
| `setupjirauser`        | Set the jira username          |
| `setupjirakeychain`    | Set the Apple Keychain service where your JIRA password is stored |
| `setupjirasprintboard` | Set the Greenhopper Board Id |
| `setupjiratest`        | Test the connection|

# TODO

## v1.1
- [x] List the sprints
- [x] Show menu with story data
- [x] List subtasks of a given story
- [x] Show the assigned person

## Roadman
- [ ] List comments of a given story / subtask
- [ ] Provide screenshots of the usage
- [ ] Filter the listed stories
- [ ] Select the Board from Alfred and not with an ID
- [ ] Refactor the setup method to avoid code duplication
- [ ] Add a comment to a story/subtask
- [ ] Create a story
- [ ] Create a subtask 
- [ ] Search by name
- [ ] Search by Key