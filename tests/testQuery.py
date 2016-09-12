#!/usr/bin/python

import unittest
import omniture
import os

creds = {}
creds['username'] = os.environ['OMNITURE_USERNAME']
creds['secret'] = os.environ['OMNITURE_SECRET']
test_suite = 'omniture.api-gateway'
dateTo = "2015-06-01"
dateFrom = "2015-06-02"
date = dateTo


class QueryTest(unittest.TestCase):
    def setUp(self):
        self.analytics = omniture.authenticate(creds['username'], creds['secret'])
        #reportdef = self.analytics.suites[test_suite].report
        #queue = []
        #queue.append(reportdef)
        #self.report = omniture.sync(queue)


    def test_ranked(self):
        basic_report = self.analytics.suites[test_suite].report.element("page")
        queue = []
        queue.append(basic_report)
        response = omniture.sync(queue)

        for report in response:
            self.assertEqual(report.elements[0].id, "page", "The element is wrong")
            self.assertEqual(len(report.elements), 1, "There are too many elements")
            self.assertEqual(report.type, "ranked", "This is the wrong type of report it should be ranked")


    def test_report_run(self):
        self.assertIsInstance(self.analytics.suites[test_suite].report.run(), omniture.Report, "The run method doesn't work to create a report")

    #@unittest.skip("skip")
    def test_bad_element(self):
        self.assertRaises(KeyError,self.analytics.suites[test_suite].report.element, "pages")

    #@unittest.skip("skip")
    def test_overtime(self):
        basic_report = self.analytics.suites[test_suite].report.metric("orders").granularity("hour")
        queue = []
        queue.append(basic_report)
        response = omniture.sync(queue)

    #@unittest.skip("skip")
    def test_double_element(self):
        basic_report = self.analytics.suites[test_suite].report.element("page").element("browser")
        queue = []
        queue.append(basic_report)
        response = omniture.sync(queue)

        for report in response:
            self.assertEqual(report.elements[0].id,"page", "The 1st element is wrong")
            self.assertEqual(report.elements[1].id,"browser", "The 2nd element is wrong")
            self.assertEqual(len(report.elements), 2, "The number of elements is wrong")
            self.assertEqual(report.type, "ranked", "This is the wrong type of report it should be ranked")

    #@unittest.skip("skip")
    def test_elements(self):
        report = self.analytics.suites[test_suite].report.elements("page","browser").run()
        self.assertEqual(report.elements[0].id,"page", "The 1st element is wrong")
        self.assertEqual(report.elements[1].id,"browser", "The 2nd element is wrong")
        self.assertEqual(len(report.elements), 2, "The number of elements is wrong")
        self.assertEqual(report.type, "ranked", "This is the wrong type of report it should be ranked")

    #@unittest.skip("skip")
    def test_double_metric(self):
        basic_report = self.analytics.suites[test_suite].report.metric("pageviews").metric("visits")
        queue = []
        queue.append(basic_report)
        response = omniture.sync(queue)

        for report in response:
            self.assertEqual(report.metrics[0].id,"pageviews", "The 1st element is wrong")
            self.assertEqual(report.metrics[1].id,"visits", "The 2nd element is wrong")
            self.assertEqual(len(report.metrics), 2, "The number of elements is wrong")
            self.assertEqual(report.type, "overtime", "This is the wrong type of report it should be overtime")

    #@unittest.skip("skip")
    def test_metrics(self):
        report = self.analytics.suites[test_suite].report.metrics("pageviews", "visits").run()
        self.assertEqual(report.metrics[0].id,"pageviews", "The 1st element is wrong")
        self.assertEqual(report.metrics[1].id,"visits", "The 2nd element is wrong")
        self.assertEqual(len(report.metrics), 2, "The number of elements is wrong")
        self.assertEqual(report.type, "overtime", "This is the wrong type of report it should be overtime")

    #@unittest.skip("skip")
    def test_element_paratmers(self):
        """Test the top and startingWith parameters
        This isn't a conclusive test. I really should run to two reports and compare the results to make sure it is corrent
        However, these tests need to be able run on any report suite and some reports suites (like ones that are currenly being
        used) don't have 10 items in the page name
        """
        basic_report = self.analytics.suites[test_suite].report.element("page", top=5, startingWith=5)
        queue = []
        queue.append(basic_report)
        response = omniture.sync(queue)

        for report in response:
            self.assertEqual(report.elements['page'].id, "page" ,"The parameters might have screwed this up")

    @unittest.skip("don't have this one done yet")
    def test_anamoly_detection(self):
        basic_report = self.analytics.suites[test_suite].report.metric("pageviews").range(dateFrom, dateTo).anomaly_detection()
        queue = []
        queue.append(basic_report)
        response = omniture.sync(queue)

        for report in response:
            self.assertEqual(report.metrics, "upper bound" ,"Anomaly Detection isn't working")

    #@unittest.skip("skip")
    def test_sortBy(self):
            """ Make sure sortBy gets put in report description """
            basic_report = self.analytics.suites[test_suite].report.element('page').metric('pageviews').metric('visits').sortBy('visits')
            self.assertEqual(basic_report.raw['sortBy'], "visits")

    #@unittest.skip("skip")
    def test_current_data(self):
        """ Make sure the current data flag gets set correctly """
        basic_report = self.analytics.suites[test_suite].report.element('page').metric('pageviews').metric('visits').currentData()
        self.assertEqual(basic_report.raw['currentData'], True)

    #@unittest.skip("skip")
    def test_inline_segments(self):
        """ Make sure inline segments work """
        report = self.analytics.suites[test_suite].report.element('page').metric('pageviews').metric('visits').filter(element='page', selected=["test","test1"])
        self.assertEqual(report.raw['segments'][0]['element'], "page", "The inline segment element isn't getting set")
        self.assertEqual(report.raw['segments'][0]['selected'], ["test","test1"], "The inline segment selected field isn't getting set")

    #@unittest.skip("skip")
    def test_hour_granularity(self):
        """ Make sure granularity works """
        report = self.analytics.suites[test_suite].report.granularity('hour')
        self.assertEqual(report.raw['dateGranularity'], "hour", "Hourly granularity can't be set via the granularity method")

    #@unittest.skip("skip")
    def test_day_granularity(self):
        """ Make sure granularity works """
        report = self.analytics.suites[test_suite].report.granularity('day')
        self.assertEqual(report.raw['dateGranularity'], "day", "daily granularity can't be set via the granularity method")

    #@unittest.skip("skip")
    def test_week_granularity(self):
        """ Make sure granularity works """
        report = self.analytics.suites[test_suite].report.granularity('day')
        self.assertEqual(report.raw['dateGranularity'], "day", "Weekly granularity can't be set via the granularity method")

    #@unittest.skip("skip")
    def test_quarter_granularity(self):
        """ Make sure granularity works """
        report = self.analytics.suites[test_suite].report.granularity('quarter')
        self.assertEqual(report.raw['dateGranularity'], "quarter", "Quarterly granularity can't be set via the granularity method")

    #@unittest.skip("skip")
    def test_year_granularity(self):
        """ Make sure granularity works """
        report = self.analytics.suites[test_suite].report.granularity('year')
        self.assertEqual(report.raw['dateGranularity'], "year", "Yearly granularity can't be set via the granularity method")

    #@unittest.skip("skip")
    def test_single_date_range(self):
        """ Make sure date range works with a single date """
        report = self.analytics.suites[test_suite].report.range(date)
        self.assertEqual(report.raw['date'], date, "Can't set a single date")

    #@unittest.skip("skip")
    def test_date_range(self):
        """ Make sure date range works with two dates """
        report = self.analytics.suites[test_suite].report.range(dateFrom,dateTo)
        self.assertEqual(report.raw['dateFrom'], dateFrom, "Start date isn't getting set correctly")
        self.assertEqual(report.raw['dateTo'], dateTo, "End date isn't getting set correctly")

    #@unittest.skip("skip")
    def test_granularity_date_range(self):
        """ Make sure granularity works in the date range app """
        report = self.analytics.suites[test_suite].report.range(dateFrom,dateTo, granularity='hour')
        self.assertEqual(report.raw['dateFrom'], dateFrom, "Start date isn't getting set correctly")
        self.assertEqual(report.raw['dateTo'], dateTo, "End date isn't getting set correctly")
        self.assertEqual(report.raw['dateGranularity'], "hour", "Hourly granularity can't be set via the range method")

    ##@unittest.skip("skip")
    def test_jsonReport(self):
        """Check the JSON deserializer"""
        report = self.analytics.suites[test_suite].report.range(dateFrom,dateTo,granularity='day')\
            .set("source","standard")\
            .metric("pageviews")\
            .metric("visits")\
            .element("page")\
            .element("sitesection", top=100, startingWith=1)\
            .set("locale","en_US")\
            .sortBy("visits")\
            .filter("All Visits")\
            .set("anomalyDetection",True)\
            .set("currentData", True)\
            .set("elementDataEncoding","utf8")

        testreport = self.analytics.suites[test_suite].jsonReport(report.json())
        self.assertEqual(report.json(),testreport.json(), "The reportings aren't deserializing from JSON the same old:{} new:{}".format(report.json(),testreport))


    def test_disable_validate_metric(self):
        """checks that the no validate flag works for metrics"""
        with self.assertRaises(omniture.InvalidReportError) as e:
            report = self.analytics.suites[test_suite].report\
                .metric("bad_metric", disable_validation=True)\
                .run()

        self.assertTrue(("metric_id_invalid" in e.exception.message),"The API is returning an error that might mean this is broken")


    def test_disable_validate_element(self):
        """checks that the no validate flag works for elements"""
        with self.assertRaises(omniture.InvalidReportError) as e:
            report = self.analytics.suites[test_suite].report\
                .element("bad_element", disable_validation=True)\
                .run()

        self.assertTrue(("element_id_invalid" in e.exception.message),"The API is returning an error that might mean this is broken")

    def test_disable_validate_segments(self):
        """checks that the no validate flag works for segments"""
        with self.assertRaises(omniture.InvalidReportError) as e:
            report = self.analytics.suites[test_suite].report\
                .filter("bad_segment", disable_validation=True)\
                .run()

        self.assertTrue(("segment_invalid" in e.exception.message),"The API is returning an error that might mean this is broken")

    def test_multiple_classifications(self):
        """Checks to make sure that multiple classificaitons are handled correctly """
        report = self.analytics.suites[test_suite].report\
            .element("page", classification="test")\
            .element("page", classification= "test2")

        self.assertEqual("test",  report.raw['elements'][0]['classification'],"The classifications aren't getting set right")
        self.assertEqual("test2",  report.raw['elements'][1]['classification'],"The second classification isn't getting set right")    

if __name__ == '__main__':
    unittest.main()
