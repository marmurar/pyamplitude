# !/usr/bin/python
# -*- coding: utf-8 -*-


import unittest
import random
from  pyamplitude.behavioralcohortsapi import BehavioralCohortsApi
from pyamplitude.apiresources import ProjectsHandler

class Test_BehavioralCohortsApi(unittest.TestCase):

    def setUp(self):

        myAPP = ProjectsHandler(project_name='',
                                api_key='',
                                secret_key='')

        self.behavioral_instance = BehavioralCohortsApi(myAPP,show_logs=False)

        # Define a valid cohortid from your Amplitude Dashboard

        self.cohortid = ''


    def _verify_cohort_health(self, cohort):
        self.assertTrue(isinstance(cohort, dict), 'error: api response type \
        should dict')
        self.assertTrue(isinstance(cohort['cohort'], dict), 'error:api response type \
        should dict')
        self.assertTrue(cohort['cohort']['id'] == self.cohortid, 'error: cohort \
        should have  id' )
        self.assertTrue(int(cohort['cohort']['size']) > 0, 'error: \
        test_get_cohort:cohort size cant be 0 ')


    def test_get_cohort(self):
        result = self.behavioral_instance.get_cohort(self.cohortid)
        self.assertTrue(result != None)
        self._verify_cohort_health(result)
        api_keys =['cohort', 'user_ids', 'amplitude_ids']
        keys = []
        for key in result.iterkeys():
            keys.append(str(key))
        self.assertTrue(len(set(keys) & set(api_keys)) == len(keys), 'error: api may \
        have changed, keys differ from expected.')

    def test_list_all_cohorts(self):
        result = self.behavioral_instance.list_all_cohorts()
        self.assertTrue(result != None)
        self.assertTrue(isinstance(result, list) ,'error:test_list_all_cohorts: \
        response not list type')
        random_cohort = random.choice(result)
        self._verify_cohort_health(random_cohort)

    def test_upload_cohort_from_ids(self):
        result = self.behavioral_instance.upload_cohort_from_ids(name='',
                                                                app_id=,
                                                                id_type='',
                                                                ids='',
                                                                owner='',
                                                                published=True)
        self.assertTrue(result['cohorts'] )

if __name__ == '__main__':
    unittest.main()
