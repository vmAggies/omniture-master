#!/usr/bin/python

import unittest
import omniture
import os
from datetime import date
import pandas
import datetime
import requests_mock


creds = {}
creds['username'] = os.environ['OMNITURE_USERNAME']
creds['secret'] = os.environ['OMNITURE_SECRET']
test_report_suite = 'omniture.api-gateway'


class ReportTest(unittest.TestCase):
    def setUp(self):
        self.analytics = omniture.authenticate(creds['username'], creds['secret'])

    def tearDown(self):
        self.analytics = None

    def test_basic_report(self):
        """ Make sure a basic report can be run
        """
        response = self.analytics.suites[test_report_suite].report.run()

        self.assertIsInstance(response.data, list, "Something went wrong with the report")

        #Timing Info
        self.assertIsInstance(response.timing['queue'], float, "waitSeconds info is missing")
        self.assertIsInstance(response.timing['execution'], float, "Execution info is missing")
        #Raw Reports
        self.assertIsInstance(response.report, dict, "The raw report hasn't been populated")
        #Check Metrics
        self.assertIsInstance(response.metrics, list, "The metrics weren't populated")
        self.assertEqual(response.metrics[0].id,"pageviews", "Wrong Metric")
        #Check Elements
        self.assertIsInstance(response.elements, list, "The elements is the wrong type")
        self.assertEqual(response.elements[0].id,"datetime", "There are elements when there shouldn't be")

        #check time range
        checkdate = date.today().strftime("%a. %e %h. %Y")
        self.assertEqual(response.period, checkdate)

        #check segmetns
        self.assertIsNone(response.segments)

        #Check Data
        self.assertIsInstance(response.data, list, "Data isn't getting populated right")
        self.assertIsInstance(response.data[0] , dict, "The data isn't getting into the dict")
        self.assertIsInstance(response.data[0]['datetime'], datetime.datetime, "The date isn't getting populated in the data")
        self.assertIsInstance(response.data[0]['pageviews'], int, "The pageviews aren't getting populated in the data")


    def test_ranked_report(self):
        """ Make sure the ranked report is being processed
        """

        ranked = self.analytics.suites[test_report_suite].report.element("page").metric("pageviews").metric("visits")
        queue = []
        queue.append(ranked)
        response = omniture.sync(queue)

        for report in response:
            #Check Data
            self.assertIsInstance(report.data, list, "Data isn't getting populated right")
            self.assertIsInstance(report.data[0] , dict, "The data isn't getting into the dict")
            self.assertIsInstance(report.data[0]['page'], str, "The page isn't getting populated in the data")
            self.assertIsInstance(report.data[0]['pageviews'], int, "The pageviews aren't getting populated in the data")
            self.assertIsInstance(report.data[0]['visits'], int, "The visits aren't getting populated in the data")

    def test_trended_report(self):
        """Make sure the trended reports are being processed corretly"""
        trended = self.analytics.suites[test_report_suite].report.element("page").metric("pageviews").granularity('hour').run()
        self.assertIsInstance(trended.data, list, "Treneded Reports don't work")
        self.assertIsInstance(trended.data[0] , dict, "The data isn't getting into the dict")
        self.assertIsInstance(trended.data[0]['datetime'], datetime.datetime, "The date isn't getting propulated correctly")
        self.assertIsInstance(trended.data[0]['page'], str, "The page isn't getting populated in the data")
        self.assertIsInstance(trended.data[0]['pageviews'], int, "The pageviews aren't getting populated in the data")

    def test_dataframe(self):
        """Make sure the pandas data frame object can be generated"""
        trended = self.analytics.suites[test_report_suite].report.element("page").metric("pageviews").granularity('hour').run()
        self.assertIsInstance(trended.dataframe, pandas.DataFrame, "Data Frame Object doesn't work")

    def test_segments_id(self):
        """ Make sure segments can be added """
        suite = self.analytics.suites[test_report_suite]
        report = suite.report.filter(suite.segments[0]).run()

        self.assertEqual(report.segments[0], suite.segments[0], "The segments don't match")

    @unittest.skip("skip inline segments because checked in Query")
    def test_inline_segment(self):
        """ Make sure inline segments work """
        #pretty poor check but need to make it work with any report suite
        report = self.analytics.suites[0].report.element('page').metric('pageviews').metric('visits').filter(element='browser', selected=["::unspecified::"]).run()
        self.assertIsInstance(report.data, list, "inline segments don't work")

    @requests_mock.mock()
    def test_multiple_classifications(self, m):
        """Makes sure the report can parse multiple classifications correctly since they have the same element ID"""
        #load sample file
        path = os.path.dirname(__file__)

        with open(path+'/mock_objects/multi_classifications.json') as data_file:
            json_response = data_file.read()

        with open(path+'/mock_objects/Report.Queue.json') as queue_file:
            ReportQueue = queue_file.read()

        #setup mock object
        m.post('https://api.omniture.com/admin/1.4/rest/?method=Company.GetReportSuites', text=json_response)
        m.post('https://api.omniture.com/admin/1.4/rest/?method=Report.Get', text=json_response)
        m.post('https://api.omniture.com/admin/1.4/rest/?method=Report.Queue', text=ReportQueue)

        report = self.analytics.suites[0].report\
            .element('evar2',classification="Classification 1", disable_validation=True)\
            .element('evar2',classification="Classification 2", disable_validation=True)\

        report = report.run()

        self.assertTrue('evar2 | Classification 1' in report.data[0], "The Value of report.data[0] was:{}".format(report.data[0]))
        self.assertTrue('evar2 | Classification 2' in report.data[0], "The Value of report.data[0] was:{}".format(report.data[0]))

    @requests_mock.mock()
    def test_mixed_classifications(self, m):
        """Makes sure the report can parse reports with classifications and
        regular dimensionscorrectly since they have the same element ID"""
        #load sample file
        path = os.path.dirname(__file__)

        with open(path+'/mock_objects/mixed_classifications.json') as data_file:
            json_response = data_file.read()

        with open(path+'/mock_objects/Report.Queue.json') as queue_file:
            ReportQueue = queue_file.read()

        #setup mock object
        m.post('https://api.omniture.com/admin/1.4/rest/?method=Company.GetReportSuites', text=json_response)
        m.post('https://api.omniture.com/admin/1.4/rest/?method=Report.Get', text=json_response)
        m.post('https://api.omniture.com/admin/1.4/rest/?method=Report.Queue', text=ReportQueue)

        report = self.analytics.suites[0].report\
            .element('evar3',classification="Classification 1", disable_validation=True)\
            .element('evar5', disable_validation=True)\

        report = report.run()

        self.assertTrue('evar3 | Classification 1' in report.data[0], "The Value of report.data[0] was:{}".format(report.data[0]))
        self.assertTrue('evar5' in report.data[0], "The Value of report.data[0] was:{}".format(report.data[0]))



if __name__ == '__main__':
    unittest.main()
