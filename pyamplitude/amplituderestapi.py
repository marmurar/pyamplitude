# !/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import logging
import sys
import simplejson as json
from datetime import datetime
from pyamplitude.apiresources import Segment


class AmplitudeRestApi(object):
    """ AmplitudeRestApi class for Amplitude Dashboard Data.

        For more information, please read:
        https://amplitude.zendesk.com/hc/en-us/articles/205469748-Dashboard-Rest-API-Export-Amplitude-Dashboard-Data

        NOTE: Each method will proceed with the following procedure:

         cast-parameters -> calculate query cost -> execute requests

    """

    ERROR_CODES = ['401','400','429','500']

    def __init__(self, project_handler, show_logs, show_query_cost):

        self.project_handler = project_handler
        self.api_url         = 'https://amplitude.com/api/2/'
        self.logger          = self._logger_config(show_logs)
        self.show_query_cost = show_query_cost

    @staticmethod
    def _logger_config(show_logs):
        """A static method configuring logs"""

        if show_logs:
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            logger.disabled = False
            return logger
        else:
            logger = logging.getLogger()
            logger.disable  = True
            logger.propagate = False

        return logger

    def _check_date_parameters(self, start, end):
        """ Used to check start_date and end_date format parameters."""
        dates = start + end

        if not dates.isdigit():
            self.logger.error('AmplitudeRestApi:_check_date_parameters:         \
            + parameter start and day should be in format: ')
            return False
        try:
            start = datetime.strptime(start, "%Y%m%d")
            end   = datetime.strptime(end, "%Y%m%d")
            if end < start:
                self.logger.error('AmplitudeRestApi:_check_date_parameters:     \
                start date must begin before end date')
                return False
        except e:
            self.logger.error("AmplitudeRestApi:_check_date_parameters: " + e.message)
            return False

        return True

    def _calculate_number_of_days(self, start_date, end_date):
        """ Caculates # of days: This is the number of days you are querying over."""
        number_of_days = abs((datetime.strptime(end_date, "%Y%m%d") \
                            - datetime.strptime(start_date, "%Y%m%d")).days)

        if number_of_days == 0:
            number_of_days = 1

        return number_of_days

    def _calculate_cost_for_query_type(self, endpoint):
        """ Calculates cost for the query type: Different chart types will have
        different costs. For all other endpoints not listed below, the cost is 1."""

        endpoints_costs = {'segmentation':1, 'funnels':2,
                           'retention':8, 'users':4}

        if endpoint not in endpoints_costs.keys():
            endpoints_costs = 1
        else:
            endpoints_costs = endpoints_costs[endpoint]

        return endpoints_costs

    def _calculate_number_of_conditions(self, segment_definitions):
        """ # of conditions: This is the number of segments + the number of
            conditions within the segments applied to the chart you are looking at.
            In addition, each group by will count as 4 segments. For example, the
            following configuration will generate 10 because we have 1 segment with
            1 condition and 2 group bys applied """

        number_of_conditions = 0

        if segment_definitions is None:
            number_of_conditions = 1

        return number_of_conditions

    def _make_request(self, url):
        """ Each AmplitudeRestAPI method return data by using _make_request"""
        try:
            response = requests.get(url, auth=(self.project_handler.api_key,
                                               self.project_handler.secret_key))

            error_message = 'Pyamplitude Error: '  + str(response.text)

            if response.status_code not in  AmplitudeRestApi.ERROR_CODES:
                data = json.loads(response.text)
                return data
            else:
                error_message = 'Pyamplitude Error: An error ocurred when decoding requests response to json'
                self.logger.warn(error_message)

                raise Exception(error_message)
        except:
            self.logger.warn(error_message)
            return Exception(error_message)

    def _validate_group_by_clause(self, segment_definitions, group_by):
        """ Group by clause validation """
        if group_by is not None:
            if segment_definitions == None:
                raise ValueError('Pyamplitude Error: Impossible to group by data without a segment definition')
            for prop in group_by:
                valid = False
                for segment in segment_definitions:
                    for filter_ in segment.get_filters():
                        if filter_['prop'] == prop:
                            valid = True
                            break
                if not valid:
                    error_message = 'Pyamplitude Error: Group by property not cointained in any filters from  the segment propertyes'
                    self.logger.error(error_message)
                    raise ValueError(error_message)

    def _validate_segments_definition(self, segment_definitions):
        # First validation: segment_definition must not be None
        if segment_definitions is not None:
            # Second Validation: segment must not be empty
            if len(segment_definitions) == 0:
                error_message = 'Pyamplitude Error: Segment MUST NOT be empty'
                raise ValueError(error_message)
            # Third Validation: Segment definition content must be a segment definition
            for segment in segment_definitions:
                if not isinstance(segment, Segment):
                    error_message = 'Pyamplitude Error: Segment definition content must be a segment definition'
                    raise ValueError(error_message)


    def _calculate_query_cost(self,
                              start_date,
                              end_date,
                              endpoint,
                              segment_definitions):
        """ Calculate your query cost for each endpoint.

        The User Activity and User Search endpoints have a different concurrent
        and rate limit than all other request types.

        Concurrent Limit: You can only run up to 5 concurrent requests.
        Rate Limit: You can run up to 360 queries per hour.

        All Other Endpoints

        All other endpoints take into account a concept of cost per query.
        We calculate cost based on the following formula:

        cost = (# of days) * (# of conditions) * (cost for the query type)
        """
        number_of_days       = self._calculate_number_of_days(start_date,end_date)
        number_of_conditions = self._calculate_number_of_conditions(segment_definitions)
        cost_for_query_type  = self._calculate_cost_for_query_type(endpoint)

        total_query_cost = number_of_days * cost_for_query_type * number_of_conditions

        return total_query_cost

    def get_active_and_new_user_count(self,
                                      start,
                                      end,
                                      m                   = 'active',
                                      interval            = 1,
                                      segment_definitions = [],
                                      group_by            = None):

        """ Get the number of active or new users.

        Returns:
                xValues: An array of (string) dates formatted like "YYYY-MM-DD"
                with one for each in the specified date range.
                series:	 An array with one element which is itself an array that
                contains the average session length for each day.
        """

        if segment_definitions is None and group_by is not None:
            raise ValueError('Pyamplitude Error: Segment_definition & group_by must be defined...')

        if not self._check_date_parameters(start=start, end=end):
           raise ValueError('Pyamplitude Error: Check start & end date parameters...')

        if m != 'new' and m != 'active':
            message = 'Pyamplitude Error: get_active_and_new_user_count: + parameter: m must be "'"active"'"  or "'"new"'" '
            self.logger.error(error_message)
            raise ValueError(error_message)

        if interval not in [1,7,30]:
            error_message = 'Pyamplitude Error: get_active_and_new_user_count: + parameter: i must be Either 1, 7, or 30 for daily, weekly, and  monthly counts, respectively (default: 1)'
            self.logger.error(error_message)
            raise ValueError(error_message)

        self._validate_group_by_clause(segment_definitions, group_by)
        self._validate_segments_definition(segment_definitions)

        endpoint = 'users'

        if self.show_query_cost:
            query_cost = self._calculate_query_cost(start_date          = start,
                                                    end_date            = end,
                                                    endpoint            = endpoint,
                                                    segment_definitions = segment_definitions)

            print("Calculated query cost: " , query_cost)

        url = self.api_url + endpoint + '?start=' + start + '&end=' + end + '&m=' + m + '&i=' + str(interval)

        if segment_definitions is not None:
            url += '&s=' + str(segment_definitions)

        if group_by is not None:
            for prop in group_by:
                url += '&g=' + str(prop)

        api_response = self._make_request(url)

        return api_response

    def get_session_length_distribution(self,
                                        start,
                                        end):
        """ Get the number of sessions for each pre-defined length ("bucket")
        period during a specified date range.

        Returns:
                xValues: An array of (string) dates formatted like "YYYY-MM-DD"
                with one for each in the specified date range.
                series:	 An array with one element which is itself an array that
                contains the (float) average number of sessions per user for
                each day.
                """

        endpoint = 'sessions'

        url = self.api_url + endpoint + '/length' + '?start=' + start + '&end=' + end

        if not self._check_date_parameters(start=start, end=end):
           raise ValueError('Pyamplitude Error: Check start & end date parameters...')


        if self.show_query_cost:
            query_cost = self._calculate_query_cost(start_date = start,
                                                    end_date   = end,
                                                    endpoint   = endpoint,
                                                    segment_definitions = None)

            print("Calculated query cost: " , query_cost)

        api_response = self._make_request(url)

        return api_response

    def get_average_session_length(self,
                                   start,
                                   end):
        """ Get the average session length (in seconds) for each day in the
        specified date range."""

        endpoint = 'sessions'

        url = self.api_url + endpoint + '/average?start=' + start + '&end=' + end

        if not self._check_date_parameters(start=start,end=end):
           raise ValueError('Pyamplitude Error:  Wrong date parameters...')

        if self.show_query_cost:
            query_cost = self._calculate_query_cost(start_date = start,
                                                    end_date   = end,
                                                    endpoint   = endpoint,
                                                    segment_definitions = None)

            print("Calculated query cost: " , query_cost)

        api_response = self._make_request(url)

        return api_response

    def get_average_session_per_user(self, start, end):
        """ Get the average number of sessions per user on each day in the
        specified date range.."""

        endpoint = 'sessions'

        url = self.api_url + endpoint + '/peruser?start=' + start + '&end=' + end

        if not self._check_date_parameters(start=start,end=end):
           raise ValueError('Pyamplitude Error:  Wrong date parameters...')

        if self.show_query_cost:
            query_cost = self._calculate_query_cost(start_date = start,
                                                    end_date   = end,
                                                    endpoint   = endpoint,
                                                    segment_definitions = None)

            print("Calculated query cost: " , query_cost)

        api_response = self._make_request(url)

        return api_response

    def get_user_composition(self,
                             start,
                             end,
                             proper=[]):
        """
           Get the distribution of users across values of a user property in the
           specified date range.

           Args:
                start (required)	First date included in data series,
                formatted YYYYMMDD (e.g. "20141001").
                end (required)	Last date included in data series,
                formatted YYYYMMDD (e.g. "20141004").p (required)

               The property to get the composition of.For built-in Amplitude
               properties,valid values are version, country, city, region, DMA,
               language,platform, os, device, start_version,and paying.

               For custom-defined user properties, the value should be
               formatted as "gp:name" (e.g. "gp:age").
        """
        if not self._check_date_parameters(start=start,end=end):
           raise ValueError('Pyamplitude Error: _check_date_parameters:Wrong date parameters...')

        composition_options = ['version','country','city','region','DMA',
                               'lenguage','platform', 'os', 'device',
                               'start_version', 'paying']

        if proper not in composition_options and 'gp:' not in str(proper):
            pass
        else:
            self.logger.exception('Pyamplitude Error: Bad defined property')

        endpoint = 'composition'

        aux = 0
        data = ''
        for x in proper:
            data += '&p=' + x

        url = self.api_url + endpoint + '?start=' + start + '&end=' + end + data

        if self.show_query_cost:
            query_cost = self._calculate_query_cost(start_date = start,
                                                    end_date   = end,
                                                    endpoint   = endpoint,
                                                    segment_definitions = None)

            print("Calculated query cost: " , query_cost)

        api_response = self._make_request(url)

        return api_response

    def get_events(self,
                   start,
                   end,
                   event_name=[],
                   mode='totals',
                   interval='1'):
        """ Get totals, uniques, averages, or DAU for multiple events at once.

        Args:
                event_name (required, multiple)	Names of the events to retrieve data for.

                mode (optional)	Either "totals", "uniques", "avg", or "pct_dau"
                to get the desired metric (default: "totals").

                start (required)	First date included in data series,
                formatted YYYYMMDD (e.g. "20141001")

                end (required)	Last date included in data series,
                formatted YYYYMMDD (e.g. "20141004")

                interval (optional)	Either 1, 7, or 30 for daily, weekly, and
                monthly counts, respectively (default: 1).
        """

        if not self._check_date_parameters(start=start,end=end):
           raise ValueError('Pyamplitude Error: _check_date_parameters:Wrong date parameters...')

        endpoint = 'events'
        mode_options = ['totals','uniques','avg','pct_dau']

        events = []
        if len(event_name) == 1:
            events = str(event_name[0]).replace(' ','%')
        else:
            for x in event_name:
                events.append(str(x).replace(' ','%'))

        if mode not in mode_options:
            self.logger.warn('Pyamplitude Error: invalid option for m parameter, options: totals,paying,arpu,arppu')

        url = self.api_url + endpoint + '?e=' + str(events) + '&start=' + start + '&end=' + end + '&m=' + mode + '&i=' + interval


        if self.show_query_cost:
            query_cost = self._calculate_query_cost(start_date = start,
                                                    end_date   = end,
                                                    endpoint   = endpoint,
                                                    segment_definitions = None)

            print("Calculated query cost: " , query_cost)

        api_response = self._make_request(url)

        return api_response

    def get_event_list(self):
        """ Get the list of events with the current week's totals, uniques, and
         DAU.

         Returns:

                The response contains an array with one element per event.
                Each event has the following fields:

                Attribute	      Description

                name	          Name of the event.

                totals	          The total number of times the event has been
                                  performed this week.
        """
        endpoint = 'events'
        url = self.api_url + endpoint + '/list'

        api_response = self._make_request(url)

        return api_response

    def get_user_activity(self,
                          user='',
                          offset='',
                          limit=''):
        """ Get a user summary and their most recent 1000 events plus the rest
        of the events contained in the session at the end.

        Args:

            user (required)	Amplitude ID of the user.

            offset (optional)	Zero-indexed offset to start returning events from.

            limit (optional)	Limit on number of events returned (up to 1000).

        Returns:

            events:	An array of JSON objects, one for each event performed by
            the user.

            userData: Aggregate statistics about the user and their user
            properties.

        """

        endpoint = 'useractivity'

        if self.show_query_cost:
            query_cost = self._calculate_query_cost(start_date = start,
                                                    end_date   = end,
                                                    endpoint   = endpoint,
                                                    segment_definitions = None)

            print("Calculated query cost: " , query_cost)

        url = self.api_url + endpoint + '?user=' + user

        api_response = self._make_request(url)

        return api_response

    def get_user_search(self, user=''):
        """ Search for a user with a specified Amplitude ID, Device ID, User ID,
         or User ID prefix.

         Args:
                user (required)	Amplitude ID, Device ID, User ID, or User ID
                prefix.
        Returns:
                matches: An array of JSON objects, one for each matching user
                containing their Amplitude ID and User ID.
                type: Which match type (Amplitude ID, Device ID, User ID, User ID
                prefix) yielded the result.
        """

        endpoint = 'usersearch'

        url = self.api_url + endpoint + '?user=' + user

        api_response = self._make_request(url)

        return api_response

    def get_realtime_active_users(self,
                                  interval=5):
        """ Get active user numbers with minute granularity for the last two
        days.

        Args:
                Parameter	Description
                i (optional)	Length of time interval. The only option
                available is 5 for realtime, which is also the default.


        Returns:
                xValues	An array of (string) times in the form "HH:mm", one for
                each time interval in a day starting from the current time.

                seriesLabels	An array of two labels: "Today" and "Yesterday".

                series	An array with one element for each group, in the same
                order as "seriesLabels", where each element is itself an array
                that contains the value of the metric on each of the days
                specified in "xValues".
        """

        endpoint = 'realtime'


        if self.show_query_cost:
            query_cost = self._calculate_query_cost(start_date = start,
                                                    end_date   = end,
                                                    endpoint   = endpoint,
                                                    segment_definitions = None)

            print("Calculated query cost: " , query_cost)

        url = self.api_url + endpoint + '?i=' + str(interval)

        api_response = self._make_request(url)

        return api_response

    def get_revenue_analysis(self,
                             start,
                             end,
                             interval='1',
                             m='total',
                             segment_definitions=None,
                             group_by=None):
        """ Get revenue metrics by day/week/month

        Args:
                m (optional)	One of the following metrics: "total", "paying",
                "arpu", or "arppu" (default: "total").

                start (required)	First date included in data series,
                formatted YYYYMMDD (e.g. "20141001").

                end (required)	Last date included in data series,
                formatted YYYYMMDD (e.g. "20141004").

                i (optional)	Either 1, 7, or 30 for daily, weekly, and
                monthly counts, respectively (default: 1).
                s (optional)	Segment definitions (default: none).
                Full description.
                g (optional)(up to 1)	The property to group by (default: none).
                Full description.

        Returns:
                xValues	An array of (string) times in the form "HH:mm", one for
                each time interval in a day starting from the current time.

                seriesLabels	An array of two labels: "Today" and "Yesterday".

                series	An array with one element for each group, in the same
                order as "seriesLabels", where each element is itself an array
                that contains the value of the metric on each of the days
                specified in "xValues".
        """

        endpoint = 'revenue'

        if not self._check_date_parameters(start=start,end=end):
           raise ValueError('Pyamplitude Error: Wrong date parameters...')

        m_options = ["total", "paying", "arpu", "arppu"]

        if m not in m_options:
            self.logger.warn('Pyamplitude Error:  invalid option for m   \
            parameter, options: totals,paying,arpu,arppu')

        self._validate_group_by_clause(segment_definitions, group_by)
        self._validate_segments_definition(segment_definitions)

        if self.show_query_cost:
            query_cost = self._calculate_query_cost(start_date = start,
                                                    end_date   = end,
                                                    endpoint   = endpoint,
                                                    segment_definitions = None)

            print("Calculated query cost: " , query_cost)

        url = self.api_url + endpoint + '/day' + '?m=' + m + '&start=' + start + '&end=' \
        + end + '&i=' + str(interval)

        if segment_definitions is not None:
            url += '&s=' + str(segment_definitions)

        if group_by is not None:
            for prop in group_by:
                url += '&g=' + str(prop)

        api_response = self._make_request(url)

        return api_response

    def get_revenue_ltv(self,
                        start,
                        end,
                        interval='1',
                        m='0',
                        segment_definitions=None,
                        group_by=None):

        """ Get the lifetime value of new users.

        Args:
            m (optional)	One of the following metrics: 0 = ARPU, 1 = ARPPU,
            2 = Total Revenue, 3 = Paying Users (default 0).

            start (required)	First date included in data series, formatted
            YYYYMMDD (e.g. "20141001").

            end (required)	Last date included in data series, formatted
            YYYYMMDD (e.g. "20141004").

            i (optional)	Either 1, 7, or 30 for daily, weekly, and monthly
            counts, respectively (default: 1).

            s (optional)	Segment definitions (default: none).
            Full description.

            g (optional)(up to 1)	The property to group by (default: none).
            Full description.

        Returns:
            seriesLabels	An array of labels, one for each group.

            series	A JSON object containing two keys:

            "dates" - An array of formatted string dates, one for each date in
            the specified range (in descending order).

            "values" - A JSON object with one key for each date, where each
            value is a JSON object with keys "r1d", "r2d", ..., "r90d" for the
            n-day metric values as well as the keys "count", "paid", and
            "total_amount", indicating the total number of users, number of
            paid users, and amount paid by the users for the group.

        """

        endpoint = 'revenue'
        m_options = ['0','1','2','3']

        if self.show_query_cost:
           query_cost = self._calculate_query_cost(start_date = start,
                                                   end_date   = end,
                                                   endpoint   = endpoint,
                                                   segment_definitions = None)

           print("Calculated query cost: ", query_cost)

        if m not in m_options:
            self.logger.warn('Pyamplitude Error: invalid option for m   \
            One of the following metrics: 0 = ARPU, 1 = ARPPU 2 = Total Revenue, \
            3 = Paying Users (default 0).')

        if not self._check_date_parameters(start=start, end=end):
           raise ValueError('Pyamplitude Error:  Check date parameters...')

        self._validate_group_by_clause(segment_definitions, group_by)
        self._validate_segments_definition(segment_definitions)


        url = self.api_url + endpoint + '/' + 'ltv?m=' + str(m) + '&start=' + start + '&end=' \
        + end + '&i=' + str(interval)

        if segment_definitions is not None:
            url += '&s=' + str(segment_definitions)

        if group_by is not None:
            for prop in group_by:
                url += '&g=' + str(prop)

        api_response = self._make_request(url)

        return api_response

    def get_annotations(self):
        """ Get the annotations configured in the app.

            Returns:
                    The response contains an array with one element per
                    annotation.

                    Each annotation has the following fields:

                    Attribute	Description

                    label	The label of the annotation.
                    date	The date (in YYYY-MM-DD format) of the annotation.
                    details	Details associated with the annotation.
        """

        endpoint = 'annotations'

        if self.show_query_cost:
            query_cost = self._calculate_query_cost(start_date = start,
                                                    end_date   = end,
                                                    endpoint   = endpoint,
                                                    segment_definitions = None)

            print("Calculated query cost: " , query_cost)

        url = self.api_url + endpoint

        api_response =  self._make_request(url)

        return api_response

