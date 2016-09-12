# python-omniture


`python-omniture` is a wrapper around the Adobe Analytics API.

It is not meant to be comprehensive. Instead, it provides a high-level interface
to certain many of the common reporting queries, and allows you to do construct other queries
closer to the metal.

## Installation

Through PyPI (older version):

    pip install omniture
    
    pip install git+https://github.com/vmAggies/omniture-master.git

## Authentication

The most straightforward way to authenticate is with:

```python
    import omniture
    analytics = omniture.authenticate('my_username', 'my_secret')
```

However, to avoid hardcoding passwords, instead you can also put your username
and password in unix environment variables (e.g. in your `.bashrc`):

```bash
    export OMNITURE_USERNAME=my_username
    export OMNITURE_SECRET=my_secret
```

With your credentials in the environment, you can then log in as follows:

```python
    import os
    import omniture
    analytics = omniture.authenticate(os.environ)
```

## Account and suites

You can very easily access some basic information about your account and your
reporting suites:

```python
    print analytics.suites
    suite = analytics.suites['reportsuite_name']
    print suite
    print suite.metrics
    print suite.elements
    print suite.segments
```

You can refer to suites, segments, elements and so on using both their
human-readable name or their id. So for example `suite.metrics['pageviews']` and `suite.metrics['Page Views']` will work exactly the same. This is especially useful in cases when segment or metric identifiers are long strings of gibberish. That way you don't have to riddle your code with references to `evar16` or `event4` and instead can call them by their title. Just remember that if you change the friendly name in the interface it will break your script.

## Running a report

`python-omniture` can run ranked, trended and over time reports. Pathing reports are still in the works

Here's a quick example:

```python
    report = suite.report \
        .element('page') \
        .metric('pageviews') \
        .run()
```
This will generate the report definition and run the report. You can alternatively generate a report definition and save the report defintion to a variable by omitting the call to the `run()` method

If you call `print` on the report defintion it will print out the JSON that you can use in the [API explorer](https://marketing.adobe.com/developer/en_US/get-started/api-explorer) for debugging or to use in other scripts

```python
    report = suite.report \
        .element('page') \
        .metric('pageviews') \

    print report
```

### Report Options
Here are the options you can add to a report.

**element()** - `element('element_id or element_name', **kwargs)` Adds an element to the report. If you need to pass in additional information in to the element (e.g. `top` or `startingWith` or `classification`) you can use the kwargs to do so. A full list of options available is documented [here](https://marketing.adobe.com/developer/en_US/documentation/analytics-reporting-1-4/r-reportdescriptionelement). If multiple elements are present then they are broken-down by one another

_Note: to disable the ID check add the parameter `disable_validation=True`_

**breakdown()** - `breakdown('element_id or element_name', **kwargs)` Same as element. It is included to make report queries more readable when there are multiple element. Use when there are more than one element. eg.

```python
    report = suite.report.element('evar1').breakdown('evar2')
```

_Note: to disable the ID check add the parameter `disable_validation=True`_

**metric()** - `metric('metric')` Adds a metric to the report. Can be called multiple times to add multiple metrics if needed.

_Note: to disable the ID check add the parameter `disable_validation=True`_

**range()** - `range('start', 'stop=None', 'months=0', 'days=0', 'granularity=None')` Sets the date range for the report. All dates shoudl be listed in ISO-8601 (e.g. 'YYYY-MM-DD')

* **Start**  --  Start date for the report. If no stop date is specified then the report will be for a single day
* **Stop** -- End date for the report.
* **months** -- Number of months back to run the report
* **days** -- Number of days back from now to run the report
* **granularity** -- The Granularity of the report (`hour`, `day`, `week`, `month`)

**granularity()** -- `granularity('granularity')` Set the granularity of the report

**sortBy()** -- `sortBy('metric')` Set the sortBy metric

**filter()** -- `filter('segment')` or `filter(element='element', selected=[])` Set the segment to be applied to the report. Can either be an segment id/name or can be used to define an inline segment by specifying the paramtered. You can add multiple filters if needed and they will be stacked (anded together)
```python
    report = suite.report.filter('537d509ee4b0893ab30616c7')
    report = suite.report.filter(element='page', selected=['homepage'])
    report = suite.report.filter('537d509ee4b0893ab30616c7')\
        .filter(element='page', selected=['homepage'])
```
_Note: to disable the ID check add the parameter `disable_validation=True`_

**currentData()** --`currentData()` Set the currentData flag

**run()** -- `run(defaultheartbeat=True)` Run the report and check the queue until done. The `defaultheartbeat` writes a . (period) out to the console each time it checks on the report.


**set()** -- `set(key, value)` Set a custom attribute in the report definition

## Using the Results of a report

To see the raw output of a report.
```python
    print report
```

If you need an easy way to access the data in a report:

```python
    data = report.data
```

This will generate a list of dicts with the metrics and elements called out by id.


### Pandas Support
`python-omniture` can also generate a data frame of the data returned. It works as follows:

```python
   df = report.dataframe
```

Pandas Data frames can be useful if you need to analyize the the data or transform it easily.

### Getting down to the plumbing.

This module is still in beta and you should expect some things not to work. In particular, pathing reports have not seen much love (though they should work), and data warehouse reports don't work at all.

In these cases, it can be useful to use the lower-level access this module provides through `mysuite.report.set` -- you can pass set either a key and value, a dictionary with key-value pairs or you can pass keyword arguments. These will then be added to the raw query. You can always check what the raw query is going to be with the by simply printing the qeury.

```python
    query = suite.report \
        .element('pages')
        .metric('pageviews)
        .set(anomalyDetection='month')


    print query
```


### JSON Reports
The underlying API is a JSON API. At anytime you can get a string representation of the report that you are created by calling report.json().

```python
    json_string = suite.report.element('pageviews').json()
```

That JSON can be used in the [API explorer](https://marketing.adobe.com/developer/api-explorer). You have have it formatted nice and printed out without the unicode representations if you use the following

```python
    print suite.report.element('pageviews')
```

You can also create a report from JSON or a string representation of JSON.

```python
    report = suite.jsonReport("{'reportDescription':{'reportSuiteID':'foo'}}")
```

These two functions allow you to serialize and unserialize reports which can be helpful to re-run reports that error out.


### Removing client side validation to increase performance
The library checks to make sure the elements, metrics and segments are all valid before submitting the report to the server. To validate these the library will make an API call to get the elements, metrics and segments. The library is pretty effecient with the API calls meaning it will only request them when needed and it will cache the request for subsequent calls. However, if you are running a script on a daily basis the with the same metrics, dimensions and segments this check can be redundant, especially if you are running reports across multiple report suites. To disable this check you woudl add the `disable_validation=True` parameter to the method calls. Here is how you would do it.

```python

suite.report.metric("page",disable_validation=True).run()
suite.report.element("pageviews",disable_validation=True).run()
suite.report.filter("somesegmentID",disable_validation=True).run()

```

One thing to note is that this method only support the IDs and not the friendly names and it still requires that those IDs be valid (the server still checks them).



### Running multiple reports

If you're interested in automating a large number of reports, you can speed up the
execution by first queueing all the reports and only _then_ waiting on the results.

Here's an example:

```python
    queue = []
    for segment in segments:
        report = suite.report \
            .range('2013-05-01', '2013-05-31', granularity='day') \
            .metric('pageviews') \
            .filter(segment=segment)
        queue.append(report)

    heartbeat = lambda: sys.stdout.write('.')
    reports = omniture.sync(queue, heartbeat)

    for report in reports:
        print report.segment
        print report.data

```

`omniture.sync` can queue up (and synchronize) both a list of reports, or a dictionary.

### Making other API requests
If you need to make other API requests that are not reporting reqeusts you can do so by
calling `analytics.request(api, method, params)` For example if I wanted to call
Company.GetReportSuites I would do

```python
    response = analytics.request('Company', 'GetReportSuites')
```

### Contributing
Feel free to contribute by filing issues or issuing a pull reqeust.

#### Build
If you want to build the module

```bash
    bash build.sh
```

If you want to run unit tests

```bash
    python testAll.py
```
