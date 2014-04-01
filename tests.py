
import unittest
import json
import app


class TestV1Api(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()

    def test_confirm(self):
        rv = self.client.get("/v1/confirm")
        resp = json.loads(rv.data)
        self.assertEquals(resp, True)

    def test_register(self):
        raise NotImplementedError

    def test_approve(self):
        raise NotImplementedError

    def test_request(self):
        raise NotImplementedError

