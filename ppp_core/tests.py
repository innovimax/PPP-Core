"""Test framework for running tests of the PPP core."""

__all__ = ['PPPTestCase']

import os
import json
import tempfile
from ppp_core import app
from webtest import TestApp
from unittest import TestCase
from ppp_datamodel.communication import Request, Response

base_config = """
{
    "debug": true,
    "modules": []
}
"""

class PPPTestCase(TestCase):
    def setUp(self):
        super(PPPTestCase, self).setUp()
        self.app = TestApp(app)
        self.config_file = tempfile.NamedTemporaryFile('w+')
        os.environ['PPP_CORE_CONFIG'] = self.config_file.name
        self.config_file.write(base_config)
        self.config_file.seek(0)
    def tearDown(self):
        self.config_file.close()
        del os.environ['PPP_CORE_CONFIG']
        del self.config_file
        super(PPPTestCase, self).tearDown()

    def request(self, obj):
        if isinstance(obj, Request):
            obj = obj.as_dict()
        elif isinstance(obj, str):
            obj = json.loads(obj)
        j = self.app.post_json('/', obj).json
        return list(map(Response.from_json, j))
    def assertResponse(self, request, response):
        self.assertEqual(self.request(request), response)
    def assertResponsesIn(self, request, responses):
        self.assertTrue(all(x in response for x in self.request(request)))
    def assertResponsesCount(self, request, count):
        self.assertEqual(len(self.request(request)), count)
    def assertStatusInt(self, request, status):
        res = self.app.post_json('/', request, status='*')
        self.assertEqual(res.status_int, status)

