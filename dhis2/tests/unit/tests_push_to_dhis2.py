from django.test import TestCase
from dhis2.h033b_reporter import *
from lxml import etree
import urllib2, vcr, os, dhis2, sys

FIXTURES = os.path.abspath(dhis2.__path__[0]) + "/tests/fixtures/cassettes/"

class Test_H033B_Reporter(TestCase):

  def test_submit_report(self):
    submit_data = { 'orgUnit': "6VeE8JrylXn",
                    'completeDate': "2012-11-11T00:00:00Z",
                    'period': '201211',
                    'dataValues': [
                                    {
                                      'dataElement': 'U7cokRIptxu',
                                      'value': 100
                                    },
                                    {
                                      'dataElement': 'mdIPCPfqXaJ',
                                      'value': 99
                                    }
                                  ]
                  }
    with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
      response = H033B_Reporter.submit(submit_data)
    assert response.getcode() == 200
    assert response.geturl() == "http://dhis/api/dataValueSets"
    assert response.info().getheader('Content-type') == 'application/xml;charset=UTF-8'

    assert self.verify_values(submit_data) == True

  def verify_values(self, data):
    with vcr.use_cassette(FIXTURES + self.__class__.__name__ + "/" + sys._getframe().f_code.co_name + ".yaml"):
      query = "?dataSet=V1kJRs8CtW4&period=%s&orgUnit=%s" %(data['period'], data['orgUnit'])
      url = H033B_Reporter.URL + query
      request = urllib2.Request(url, headers=H033B_Reporter.HEADERS)
      response = urllib2.urlopen(request)
      xml = etree.fromstring(response.read())
      rows = []
      for i in xml.iterchildren():
        rows.append(i)

      assert len(rows) == len(data['dataValues'])

      for index, datavalue in enumerate(data['dataValues']):
        row = rows[index].values()
        assert datavalue['dataElement'] == row[0]
        assert str(datavalue['value']) == row[4]

      return True