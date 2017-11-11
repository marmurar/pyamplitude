# !/usr/bin/python
# -*- coding: utf-8 -*-


import logging
import sys
import requests, zipfile, StringIO

class AmplitudeExportApi(object):
    """ Export all event data for a given app that were uploaded within a
        specified range of dates. The results are returned as a zipped archive
        of JSON files, one or multiple files per hour.

        IMPORTANT NOTE: The specified date range is the time of when the event
        data was uploaded to Amplitude servers (see server_upload_time).
        The Export API is also in UTC. Data is available to export at a
        minimum within 2 hours of when our servers received it. For example, -
        data sent between 8-9PM will begin loading at 9PM and will be available
        via the Export API at 11PM. Note that there is no delay in platform
        reporting--this delay is only for data you wish to export.

        For more information please refer to:
        https://amplitude.zendesk.com/hc/en-us/articles/205406637-Export-API- \
        Export-Your-App-s-Event-Data#returns
    """

    ERROR_CODES = ['401','400','429','500']

    def __init__(self, project_handler, show_logs):

        self.api_url         = 'https://amplitude.com/api/2/export'
        self.logger          = self._logger_config(show_logs)
        self.project_handler = project_handler

    @staticmethod
    def _logger_config(show_logs):
        """A static method configuring logs"""

        if show_logs:
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            logger.disabled = False
        else:
            logger = logging.getLogger()
            logger.disable = True

        return logger



    def get_all_events_data(self, start, end):
        """ Get all events with a specific start and end date

            start (required)	First hour included in data series,
            formatted YYYYMMDDTHH (e.g. '20150201T05').
            end (required)      Last hour included in data series,
            formatted YYYYMMDDTHH (e.g. '20150203T20').

            Note: If you wish to export a whole day, then it would be from
            T00 to T23.

            Returns:

            The response is a zipped archive of JSON files, with potentially
            multiple files per hour. Note that events prior to 2014-11-12 will
            be grouped by day instead of by hour. If you request data for a
            time range during which no data has been collected for the project,
            then you will receive a 404 response from our server.

        """
        url = self.api_url + '?start=' + start + '&end=' + end

        response = requests.get(url,
                                auth=(self.project_handler.api_key,
                                      self.project_handler.secret_key),
                                stream=True)

        content = zipfile.ZipFile(StringIO.StringIO(response.content))
        data = content.extractall()

        return True
