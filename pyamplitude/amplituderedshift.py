# !/usr/bin/python
# -*- coding: utf-8 -*-


import psycopg2
import logging
import sys

class AmplitudeRedshift(object):
    """ A  python connector to query data from yours Amplitude Redshift.

    Take into consideration Redshift Best Practices when querying large
    datasets. Please refer to the following link for more information:

    https://amplitude.zendesk.com/hc/en-us/articles/206240328-Redshift-Best-Practices
    """
    def __init__(self, host='', user='' ,port='', password='', dbname='',
                 schema='', table='', show_logs=True):

        self.host = host
        self.user = user
        self.port = port.password = password
        self.dbname = dbname
        self.schema = schema
        self.table = table
        self.logger = self._logger_config(show_logs)

    @staticmethod
    def _logger_config(show_logs):
        """ A static method for log configuring"""

        if show_logs:
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            logger.disabled = False
        else:
            logger.disable = True

        return logger

    def execute_query(self, query=''):
        cur = psycopg2.connect(host=self.host, user=self.user, port=self.port,
                               password=self.password, dbname=self.dbname)

        self.logger.info('redshiftplaybook: executed query: ' + query)

        cur = cur.cursor()
        cur.execute(query)
        data = cur.fetchall()
        cur.close()

        return data

    def count_redshift_active_users(self, date, schema='', table=''):
        """ Count the Active Users on a Given Day """

        if  self.schema != schema or self.table != table:
            self.schema  = schema
            self.table = table

        query =    'SELECT COUNT(DISTINCT amplitude_id)'        \
                   + ' FROM ' + self.schema + '.' + self.table  \
                   + ' WHERE DATE(event_time)=' + "'" + date + "'" + ';'
        response = self.execute_query(query)
        response = response[0][0]

        return response

    def count_specific_user_events(self, date='', event_type ='',
                                 schema='', table=''):
        """ Users Who Did Specific Events """

        if  self.schema != schema or self.table != table:
            self.schema  = schema
            self.table = table

        query =   'SELECT COUNT(DISTINCT amplitude_id)'              \
                  + ' FROM ' + self.schema + '.events'               \
                  + ' WHERE event_type = ' + "'" + event_type + "'"  \
                  + ' AND DATE(event_time)= ' + "'" + date + "'" + ';'

        response = self.execute_query(query)
        response = response[0][0]

        return response

    def get_a_list_of_users(self, date, schema='', table=''):
        """ Obtaining a List of Users """

        if  self.schema != schema or self.table != table:
            self.schema  = schema
            self.table = table

        query =   'SELECT DISTINCT user_id'                   \
                + ' FROM ' + self.schema + '.' + self.table   \
                + ' WHERE DATE(event_time)= ' + "'" +  date + "'" + ';'

        response = self.execute_query(query)
        users = [x[0] for x in response]

        return users
