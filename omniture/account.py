from __future__ import absolute_import

import requests
import binascii
import sha
import json
from datetime import datetime, date
import logging
import uuid
import hashlib
import base64
import os

from .elements import Value, Element, Segment
from .query import Query
from . import reports
from . import utils


class Account(object):
    """ A wrapper for the Adobe Analytics API. Allows you to query the reporting API """
    DEFAULT_ENDPOINT = 'https://api.omniture.com/admin/1.4/rest/'

    def __init__(self, username, secret, endpoint=DEFAULT_ENDPOINT, cache=False, cache_key=None):
        """Authentication to make requests."""
        self.log = logging.getLogger(__name__)
        self.username = username
        self.secret = secret
        self.endpoint = endpoint
        #Allow someone to set a custom cache key
        self.cache = cache
        if cache_key:
            self.cache_key = cache_key
        else:
            self.cache_key = date.today().isoformat()
        if self.cache:
            data = self.request_cached('Company', 'GetReportSuites')['report_suites']
        else:
            data = self.request('Company', 'GetReportSuites')['report_suites']
        suites = [Suite(suite['site_title'], suite['rsid'], self) for suite in data]
        self.suites = utils.AddressableList(suites)
        #define page number as 1, will be incremented in request method. Used for warehouse requests
        self.page_num = 1

    def request_cached(self, api, method, query={}, cache_key=None):
        if cache_key:
            key = cache_key
        else:
            key = self.cache_key

        #Generate a shortened hash of the query string so that method don't collide
        query_hash = base64.urlsafe_b64encode(hashlib.md5(query).digest())

        try:
            with open(self.file_path+'/data_'+api+'_'+method+'_'+query_hash+'_'+key+'.txt') as fp:
                for line in fp:
                    if line:
                        data = ast.literal_eval(line)

        except IOError as e:
            data = self.request(api, method, query)

            # Capture all other old text files
            #TODO decide if the query should be included in the file list to be cleared out when the cache key changes
            filelist = [f for f in os.listdir(self.file_path) if f.startswith('data_'+api+'_'+method)]

            # Delete them
            for f in filelist:
                os.remove(self.file_path+'/'+f)

            # Build the new data
            the_file = open(self.file_path+'/data_'+api+'_'+method+'_'+query_hash+'_'+key+'.txt', 'w')
            the_file.write(str(data))
            the_file.close()


    def request(self, api, method, query={}):
        """
        Make a request to the Adobe APIs.

        * api -- the class of APIs you would like to call (e.g. Report,
            ReportSuite, Company, etc.)
        * method -- the method you would like to call inside that class
            of api
        * query -- a python object representing the parameters you would
            like to pass to the API
        """
        '''
        HTTP REQUEST Debugging
        try:
            import http.client as http_client
        except ImportError:
            # Python 2
            import httplib as http_client
        http_client.HTTPConnection.debuglevel = 1
        '''
        if method == 'Get' and 'reportID' in query and 'page' not in query:
            query['format'] = 'csv'
            query['page'] = self.page_num

        self.log.info("Request: %s.%s  Parameters: %s", api, method, query)
        '''
        HTTP REQUEST Debugging
        # You must initialize logging, otherwise you'll not see debug output.
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
        '''
        response = requests.post(
            self.endpoint,
            params={'method': api + '.' + method},
            data=json.dumps(query),
            headers=self._build_token()
            )
        self.log.debug("Response for %s.%s:%s", api, method, response.text)

        if method == 'Get' and 'format' in query:
            self.log.debug("Error Code %s", response.status_code)
            if response.status_code == 400:
                import json as js
                dict_Value = js.loads(response.content)
                if dict_Value['error'] == 'report_not_ready':
                    raise reports.ReportNotReadyError(response.content)
                elif dict_Value['error'] == 'eof_or_invalid_page':
                    return response
                elif dict_Value['error'] == 'no_warehouse_data':
                    return response
                elif dict_Value['error'] != None:
                    raise reports.InvalidReportError(response.content)
                else:
                    return response
            else:
                self.page_num = self.page_num + 1
                return response
        else:
            json_response = response.json()

            if type(json_response) == dict:
                self.log.debug("Error Code %s", json_response.get('error'))
                if json_response.get('error') == 'report_not_ready':
                    raise reports.ReportNotReadyError(json_response)
                elif json_response.get('error') != None:
                    raise reports.InvalidReportError(json_response)
                else:
                    return json_response
            else:
                return json_response


    def jsonReport(self, reportJSON):
        """Generates a Report from the JSON (including selecting the report suite)"""
        if type(reportJSON) == str:
            reportJSON = json.loads(reportJSON)
        suiteID = reportJSON['reportDescription']['reportSuiteID']
        suite = self.suites[suiteID]
        return suite.jsonReport(reportJSON)


    def _serialize_header(self, properties):
        header = []
        for key, value in properties.items():
            header.append('{key}="{value}"'.format(key=key, value=value))
        return ', '.join(header)

    def _build_token(self):
        nonce = str(uuid.uuid4())
        base64nonce = binascii.b2a_base64(binascii.a2b_qp(nonce))
        created_date = datetime.utcnow().isoformat() + 'Z'
        sha_object = sha.new(nonce + created_date + self.secret)
        password_64 = binascii.b2a_base64(sha_object.digest())

        properties = {
            "Username": self.username,
            "PasswordDigest": password_64.strip(),
            "Nonce": base64nonce.strip(),
            "Created": created_date,
        }
        header = 'UsernameToken ' + self._serialize_header(properties)

        return {'X-WSSE': header}

    def _repr_html_(self):
        """ Format in HTML for iPython Users """
        html = ""
        html += "<b>{0}</b>: {1}</br>".format("Username", self.username)
        html += "<b>{0}</b>: {1}</br>".format("Secret", "***************")
        html += "<b>{0}</b>: {1}</br>".format("Report Suites", len(self.suites))
        html += "<b>{0}</b>: {1}</br>".format("Endpoint", self.endpoint)
        return html

    def __str__(self):
        return "Analytics Account -------------\n Username: \
            {0} \n Report Suites: {1} \n Endpoint: {2}" \
            .format(self.username, len(self.suites), self.endpoint)


class Suite(Value):
    """Lets you query a specific report suite. """
    def request(self, api, method, query={}):
        raw_query = {}
        raw_query.update(query)
        if method == 'GetMetrics' or method == 'GetElements':
            raw_query['reportSuiteID'] = self.id

        return self.account.request(api, method, raw_query)

    def __init__(self, title, id, account, cache=False):
        self.log = logging.getLogger(__name__)
        super(Suite, self).__init__(title, id, account)
        self.account = account

    @property
    @utils.memoize
    def metrics(self):
        """ Return the list of valid metricsfor the current report suite"""
        if self.account.cache:
            data = self.request_cache('Report', 'GetMetrics')
        else:
            data = self.request('Report', 'GetMetrics')
        return Value.list('metrics', data, self, 'name', 'id')

    @property
    @utils.memoize
    def elements(self):
        """ Return the list of valid elementsfor the current report suite """
        if self.account.cache:
            data = self.request_cached('Report', 'GetElements', {"reportType":"warehouse"})
        else:
            data = self.request('Report', 'GetElements', {"reportType":"warehouse"})
        return Element.list('elements', data, self, 'name', 'id')

    @property
    @utils.memoize
    def segments(self):
        """ Return the list of valid segments for the current report suite """
        if self.account.cache:
            data = self.request_cached('Segments', 'Get',{"accessLevel":"shared"})
        else:
            data = self.request('Segments', 'Get',{"accessLevel":"shared"})
        return Segment.list('segments', data, self, 'name', 'id',)

    @property
    def report(self):
        """ Return a report to be run on this report suite """
        return Query(self)

    def jsonReport(self,reportJSON):
        """Creates a report from JSON. Accepts either JSON or a string. Useful for deserializing requests"""
        q = Query(self)
        #TODO: Add a method to the Account Object to populate the report suite this call will ignore it on purpose
        if type(reportJSON) == str:
            reportJSON = json.loads(reportJSON)

        reportJSON = reportJSON['reportDescription']

        if reportJSON.has_key('dateFrom') and reportJSON.has_key('dateTo'):
            q = q.range(reportJSON['dateFrom'],reportJSON['dateTo'])
        elif reportJSON.has_key('dateFrom'):
            q = q.range(reportJSON['dateFrom'])
        elif reportJSON.has_key('date'):
            q = q.range(reportJSON['date'])
        else:
            q = q

        if reportJSON.has_key('dateGranularity'):
            q = q.granularity(reportJSON['dateGranularity'])

        if reportJSON.has_key('source'):
            q = q.source(reportJSON['source'])

        if reportJSON.has_key('metrics'):
            for m in reportJSON['metrics']:
                q = q.metric(m['id'])

        if reportJSON.has_key('elements'):
            for e in reportJSON['elements']:
                id = e['id']
                del e['id']
                q= q.element(id, **e)

        if reportJSON.has_key('locale'):
            q = q.set('locale',reportJSON['locale'])

        if reportJSON.has_key('sortMethod'):
            q = q.set('sortMethod',reportJSON['sortMethod'])

        if reportJSON.has_key('sortBy'):
            q = q.sortBy(reportJSON['sortBy'])

        #WARNING This doesn't carry over segment IDs meaning you can't manipulate the segments in the new object
        #TODO Loop through and add segment ID with filter method (need to figure out how to handle combined)
        if reportJSON.has_key('segments'):
            q = q.set('segments', reportJSON['segments'])

        if reportJSON.has_key('anomalyDetection'):
            q = q.set('anomalyDetection',reportJSON['anomalyDetection'])

        if reportJSON.has_key('currentData'):
            q = q.set('currentData',reportJSON['currentData'])

        if reportJSON.has_key('elementDataEncoding'):
            q = q.set('elementDataEncoding',reportJSON['elementDataEncoding'])
        return q

    def _repr_html_(self):
        """ Format in HTML for iPython Users """
        return "<td>{0}</td><td>{1}</td>".format(self.id, self.title)

    def __str__(self):
        return "ID {0:25} | Name: {1} \n".format(self.id, self.title)
