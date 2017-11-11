# !/usr/bin/python
# -*- coding: utf-8 -*-

import json
import types

class Segment(object):
    """Creates a segment object for the AmplitudeRestApi class"""
    def __init__(self):
        self.filters = []

    def __str__(self):
        return json.dumps(self.filters)

    def add_filter(self, prop, op, values):

        op_options = ["is", "is not", "contains", "does not contain",
        "less", "less or equal", "greater", "greater or equal", "set is",
        "set is not"]

        if isinstance(prop, types.StringTypes) and isinstance(op, types.StringTypes) and isinstance(values, types.ListType):
           self.filters.append({'prop':prop, 'op':op, 'values':values})
           return True
        else:
            return False

    def get_filters(self):
        return self.filters

    def filter_count(self):
        return len(self.filters)


class ProjectsHandler(object):
    """ A simple access handler for Amplitude Projects"""
    def __init__(self, project_name, api_key, secret_key):
        self.project_name = project_name
        self.api_key      = api_key
        self.secret_key   = secret_key

    def __repr__(self):
        s = 'project_name: '    + self.project_name
        s += ' | api_key: '     + self.api_key
        s += ' | secret_key: '  + self.secret_key
        return s
