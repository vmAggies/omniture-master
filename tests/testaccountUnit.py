#!/usr/bin/python

import unittest
import omniture
import os

creds = {}
creds['username'] = os.environ['OMNITURE_USERNAME']
creds['secret'] = os.environ['OMNITURE_SECRET']
testReportSuite = "omniture.api-gateway"


class AccountUnitTest(unittest.TestCase):
    def setUp(self):
        self.analytics = omniture.authenticate(creds['username'], creds['secret'])

    def test_suites(self):
        self.assertIsInstance(self.analytics.suites, omniture.utils.AddressableList, "There are no suites being returned")
        self.assertIsInstance(self.analytics.suites[testReportSuite], omniture.account.Suite, "There are no suites being returned")

    def test_simple_request(self):
        """ simplest request possible. Company.GetEndpoint is not an authenticated method
        """
        urls = ["https://api.omniture.com/admin/1.4/rest/",
                "https://api2.omniture.com/admin/1.4/rest/",
                "https://api3.omniture.com/admin/1.4/rest/",
                "https://api4.omniture.com/admin/1.4/rest/",
                "https://api5.omniture.com/admin/1.4/rest/"]
        self.assertIn(self.analytics.request('Company', 'GetEndpoint'),urls, "Company.GetEndpoint failed" )

    def test_authenticated_request(self):
        """ Request that requires authentication to make sure the auth is working
        """
        reportsuites = self.analytics.request('Company','GetReportSuites')
        self.assertIsInstance(reportsuites, dict, "Didn't get a valid response back")
        self.assertIsInstance(reportsuites['report_suites'], list, "Response doesn't contain the list of report suites might be an authentication issue")

    def test_metrics(self):
        """ Makes sure the suite properties can get the list of metrics
        """
        self.assertIsInstance(self.analytics.suites[testReportSuite].metrics, omniture.utils.AddressableList)

    def test_elements(self):
        """ Makes sure the suite properties can get the list of elements
        """
        self.assertIsInstance(self.analytics.suites[testReportSuite].elements, omniture.utils.AddressableList)

    def test_basic_report(self):
        """ Make sure a basic report can be run
        """
        report = self.analytics.suites[testReportSuite].report
        queue = []
        queue.append(report)
        response = omniture.sync(queue)
        self.assertIsInstance(response, list)

    def test_json_report(self):
        """Make sure reports can be generated from JSON objects"""
        report = self.analytics.suites[testReportSuite].report.element('page').metric('pageviews').json()
        self.assertEqual(report, self.analytics.jsonReport(report).json(), "The reports aren't serializating or de-serializing correctly in JSON")

if __name__ == '__main__':
    unittest.main()
