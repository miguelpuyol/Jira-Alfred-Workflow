#!/usr/bin/env python
# encoding: utf-8
#
import os

__title__ = 'Jira-Alfred-Workflow'
__version__ = open(os.path.join(os.path.dirname(__file__), 'version')).read()
__author__ = 'Miguel Garcia Puyol'

# Main Object
from .JiraWorkflow import JiraWorkflow

# Exceptions
from .JiraWorkflow import JiraWorkflowException

# Simplified JIRA objects for caching purposes
from .JiraWorkflow import SimpleBoard

__all__ = [
    JiraWorkflow
]
