# !/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from pyamplitude.apiresources  import ProjectsHandler
from pyamplitude.amplituderestapi import AmplitudeRestApi

class Test_AmplitudeRestApi(unittest.TestCase):

    """
        Intended to be a general test veryfing the data structure from expected
        responses from those documented at the official Amplitude API
        documentation.

        For more information, please read:
        https://amplitude.zendesk.com/hc/en-us/articles/205469748-Dashboard-Rest-API-Export-Amplitude-Dashboard-Data


        Last update: Octobre 2017

    """

    def setUp(self):

        # Note: Complete with project name, api key and secret key...

        myAPP = ProjectsHandler(project_name  = '',
                                api_key       = '',
                                secret_key    = '')

        self.apiconector = AmplitudeRestApi(project_handler = myAPP,
                                            show_logs       = True,
                                            show_query_cost = False)

    def _sanity_check(self, response):
        """ General assertion tests for each Amplitude REST requests"""
        self.assertTrue(response != None)
        self.assertTrue(isinstance(response, dict), 'error: response different from dict type')

        for element in response:
            self.assertTrue(isinstance(element, unicode),'error: response is not unicode')

    def _get_response_types(self, response):

        types = []

        for x in response:
            types.append(type(response[x]))

        return types


    def test_get_active_and_new_user_count(self):

       result = self.apiconector.get_active_and_new_user_count(start         = '20170701',
                                                        end                  = '20170702',
                                                        m                    = 'active',
                                                        interval             = 1,
                                                        segment_definitions  = None,
                                                        group_by             = None)
       self.assertEqual(len(result), 1)

       self._sanity_check(response=result)

       expected_types = ['dict']
       response_types = self._get_response_types(result)

       aux = 0
       for type_element in zip(expected_types,response_types):
           self.assertTrue(str(type_element[aux]) in str(type_element[aux + 1]))


    def test_get_session_length_distribution(self):

       result = self.apiconector.get_session_length_distribution(start  = '20170701',
                                                                 end    = '20170702')

       self._sanity_check(response=result)

       expected_keys = ['withSets', 'novaRuntime', 'novaCost', 'novaRequestDuration',
                      'wasCached', 'minSampleRate', 'timeComputed', 'cacheFreshness', 'data', 'transformationIds']
       response_keys = result.keys()

       aux = 0
       for element in zip(sorted(response_keys), sorted(expected_keys)):
           self.assertTrue(str(element[aux]) == str(element[aux + 1]))


       expected_types = ['bool','int','int','int','bool','int','int','unicode','dict','list']
       response_types = self._get_response_types(result)

       aux = 0
       for type_element in zip(expected_types,response_types):
           self.assertTrue(str(type_element[aux]) in str(type_element[aux + 1]))


    def test_get_average_session_length(self):

       result = self.apiconector.get_average_session_length(start  = '20170701',
                                                            end    = '20170702')

       self._sanity_check(response=result)

       expected_keys = ['withSets','novaRuntime','novaCost','novaRequestDuration',
        'wasCached','minSampleRate','timeComputed','cacheFreshness','data', 'transformationIds']
       response_keys = result.keys()


       aux = 0
       for element in zip(sorted(response_keys),sorted(expected_keys)):
           self.assertTrue(str(element[aux]) == str(element[aux+1]))

       expected_types = ['bool', 'int', 'int', 'int', 'bool', 'int', 'int', 'unicode', 'dict', 'list']
       response_types = self._get_response_types(result)

       aux = 0
       for type_element in zip(expected_types,response_types):
           self.assertTrue(str(type_element[aux]) in str(type_element[aux + 1]))


    def test_get_user_composition(self):

       result = self.apiconector.get_user_composition(start  = '20170701',
                                                      end    = '20170702',
                                                      proper = ['country','paying'])
       self._sanity_check(response=result)

       expected_keys = ['queryIds','novaRuntime','novaCost','novaRequestDuration','wasCached','minSampleRate','timeComputed',
                      'cacheFreshness','data','transformationIds']
       response_keys = result.keys()

       aux = 0
       for element in zip(sorted(response_keys),sorted(expected_keys)):
           self.assertTrue(str(element[aux]) == str(element[aux+1]))

       expected_types = ['list','int','int','int','bool','int','int','unicode','dict','list']
       response_types = self._get_response_types(result)

       aux = 0
       for type_element in zip(expected_types,response_types):
           self.assertTrue(str(type_element[aux]) in str(type_element[aux + 1]))


    def test_get_events(self):

        result = self.apiconector.get_events(start          = '20170701',
                                             end            = '20170702',
                                             event_name     = [],
                                             mode           = 'totals',
                                             interval       = '1')

        self._sanity_check(response=result)

        expected_keys = ['novaRuntime', 'novaCost', 'novaRequestDuration', 'wasCached', 'timeComputed', 'cacheFreshness', 'data',
         'transformationIds']

        response_keys = result.keys()

        aux = 0
        for element in zip(sorted(response_keys), sorted(expected_keys)):
            self.assertTrue(str(element[aux]) == str(element[aux + 1]))

        expected_types = ['int', 'int', 'int', 'bool', 'int', 'unicode', 'dict', 'list']
        response_types = self._get_response_types(result)

        aux = 0
        for type_element in zip(expected_types, response_types):
            self.assertTrue(str(type_element[aux]) in str(type_element[aux + 1]))

    def test_get_event_list(self):

       result = self.apiconector.get_event_list()

       self._sanity_check(response=result)

       expected_types = ['int','int','int','bool','int','unicode','list','list']
       response_types = self._get_response_types(result)

       aux = 0
       for type_element in zip(expected_types,response_types):
           self.assertTrue(str(type_element[aux]) in str(type_element[aux + 1]))

       expected_keys = ['novaRuntime', 'novaCost', 'novaRequestDuration', 'wasCached', 'timeComputed',
                        'cacheFreshness','data', 'transformationIds']

       response_keys = result.keys()


       aux = 0
       for type_element in zip(expected_types,response_types):
           self.assertTrue(str(type_element[aux]) in str(type_element[aux + 1]))

    def test_get_user_activity(self):

       result = self.apiconector.get_user_activity(user='12345',offset='',limit='100')

       self._sanity_check(response=result)

       expected_types = ['dict', 'list']
       response_types = self._get_response_types(result)

       aux = 0
       for type_element in zip(expected_types,response_types):
           self.assertTrue(str(type_element[aux]) in str(type_element[aux + 1]))

       expected_keys = ['userData', 'events']

       response_keys = result.keys()

       aux = 0
       for type_element in zip(expected_types,response_types):
           self.assertTrue(str(type_element[aux]) in str(type_element[aux + 1]))


    def test_get_user_search(self):

       result = self.apiconector.get_user_search(user='12345')

       self._sanity_check(response=result)

       expected_types = ['list', 'unicode']
       response_types = self._get_response_types(result)

       aux = 0
       for type_element in zip(expected_types,response_types):
           self.assertTrue(str(type_element[aux]) in str(type_element[aux + 1]))

       expected_keys = ['matches', 'type']


       response_keys = result.keys()

       aux = 0
       for element in zip(sorted(response_keys), sorted(expected_keys)):
           self.assertTrue(str(element[aux]) == str(element[aux + 1]))

    def test_get_revenue_analysis(self):

       result = self.apiconector.get_revenue_analysis(start='20170701',
                                            end='20170702',
                                            m='total',
                                            interval=1,
                                            segment_definitions=None,
                                            group_by=None)

       self._sanity_check(response=result)

       expected_types = ['list', 'int','int','int', 'bool','int','int','unicode','dict','list']
       response_types = self._get_response_types(result)

       aux = 0
       for type_element in zip(expected_types,response_types):
           self.assertTrue(str(type_element[aux]) in str(type_element[aux + 1]))


       expected_keys = ['queryIds', 'novaRuntime', 'novaCost', 'novaRequestDuration', 'wasCached', 'minSampleRate',
        'timeComputed', 'cacheFreshness', 'data', 'transformationIds']

       response_keys = result.keys()
       aux = 0
       for element in zip(sorted(response_keys), sorted(expected_keys)):
           self.assertTrue(str(element[aux]) == str(element[aux + 1]))

    def test_get_realtime_active_users(self):

       result = self.apiconector.get_realtime_active_users(interval=5)

       self._sanity_check(response=result)

       expected_types = ['type', 'dict']
       response_types = self._get_response_types(result)

       aux = 0
       for type_element in zip(expected_types,response_types):
           self.assertTrue(str(type_element[aux]) in str(type_element[aux + 1]))


       expected_keys = ['data']

       response_keys = result.keys()
       aux = 0
       for element in zip(sorted(response_keys), sorted(expected_keys)):
           self.assertTrue(str(element[aux]) == str(element[aux + 1]))

    def test_get_annotations(self):

       result = self.apiconector.get_annotations()

       self._sanity_check(response=result)

       expected_types = ['list']
       response_types = self._get_response_types(result)

       aux = 0
       for type_element in zip(expected_types,response_types):
           self.assertTrue(str(type_element[aux]) in str(type_element[aux + 1]))

       expected_keys = ['data']

       response_keys = result.keys()
       aux = 0
       for element in zip(sorted(response_keys), sorted(expected_keys)):
           self.assertTrue(str(element[aux]) == str(element[aux + 1]))


if __name__ == '__main__':
    unittest.main()
