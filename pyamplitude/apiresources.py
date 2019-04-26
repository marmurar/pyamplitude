# !/usr/bin/python
# -*- coding: utf-8 -*-

import json

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

        if (isinstance(prop, (str,)) and
            isinstance(op, (str,)) and
            (op in op_options) and
            isinstance(values, (list,))):
           self.filters.append({'prop':prop, 'op':op, 'values':values})
           return True
        else:
            return False

    def get_filters(self):
        return self.filters

    def filter_count(self):
        return len(self.filters)
    
class Event(object):
    """Creates an event object for the AmplitudeRestApi class"""
    def __init__(self, event_type):
        self.event_type = event_type
        self.filters    = []
        self.groupby    = []
        
    def __str__(self):
        return json.dumps({"event_type": self.event_type,
                           "filters": self.filters,
                           "group_by": self.groupby
                          })
    
    def add_filter(self, subprop_type, subprop_key, subprop_op, subprop_values):
        subprop_type_options = ["event", "user"]
        subprop_op_options   = ["is", "is not", "contains", "does not contain",
                                "less", "less or equal", "greater", "greater or equal",
                                "set is", "set is not"]
        if (isinstance(subprop_type, (str,)) and
            (subprop_type in subprop_type_options) and
            isinstance(subprop_key, (str,)) and
            isinstance(subprop_op, (str,)) and
            (subprop_op in subprop_op_options) and
            isinstance(subprop_values, (list,))):
            self.filters.append({"subprop_type": subprop_type,
                                 "subprop_key": subprop_key,
                                 "subprop_op": subprop_op,
                                 "subprop_value": subprop_values})
            return True
        else:
            return False
        
    def add_groupby(self, groupby_type, groupby_value):
        groupby_type_options = ["event", "user"]
        if (isinstance(groupby_type, (str,)) and
            (groupby_type in groupby_type_options) and
            isinstance(groupby_value, (str,))):
            self.groupby.append({"type": groupby_type,
                                 "value": groupby_value})
            return True
        else:
            return False
        
    def get_filters(self):
        return self.filters
    
    def get_groupby(self):
        return self.groupby
    
    def filter_count(self):
        return len(self.filters)
    
    def groupby_count(self):
        return len(self.groupby)


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
