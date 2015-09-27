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
| `setupjirapassword`    | Saves the password in your keychain |
| `setupjirasprintboard` | Set the Greenhopper Board Id |
| `setupjiratest`        | Test the connection|

# TODO

## v0.2
- [x] List the sprints
- [x] Show menu with story data
- [x] List subtasks of a given story
- [x] Show the assigned person

## v0.3
- [x] List comments of a given story / subtask
- [x] Filter the listed stories
- [x] Search by name
- [x] Search by Key

## v0.4
- [x] Store your user and password in the Keychain via the workflow
- [ ] Select the Board from Alfred and not with an ID

## Roadmap
- [ ] Provide screenshots of the usage
- [ ] Cache jira issues and avoid hammering JIRA
- [ ] Refactor the setup method to avoid code duplication
- [ ] Add a comment to a story/subtask
- [ ] Add a comment to a story/subtask with data from the clipboard
- [ ] Create a story
- [ ] Create a subtask 
