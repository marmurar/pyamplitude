# -*- coding: utf-8 -*-
#!/usr/bin/python

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


