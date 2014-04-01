
#from mock import MagicMock
from sure import expect

import unittest
import json
import app
import yaml


class TestV1Api(unittest.TestCase):

    def setUp(self):
        app.app.config.from_object("config.TestConfig")
        app._get_db = lambda: yaml.load(open("test_data.yml"))

        self.client = app.app.test_client()

    def test_confirm_one(self):
        rv = self.client.get("/v1/confirm/hashc6id89ad98ad/jid@example.com")
        expect(json.loads(rv.data)["confirmed"]).to.be(True)

    def test_confirm_found_but_unconfirmed(self):
        rv = self.client.get("/v1/confirm/hashc6id89ad98a3/jid2@example.com")
        expect(json.loads(rv.data)["confirmed"]).to.be(False)

    def test_confirm_one_not_found(self):
        rv = self.client.get("/v1/confirm/faulty/jid@example.com")
        expect(json.loads(rv.data)["confirmed"]).to.be(False)

    def test_confirm_one_wrong_target(self):
        rv = self.client.get("/v1/confirm/hashc6id89ad98ad/jid@FAULTY.com")
        expect(json.loads(rv.data)["confirmed"]).to.be(False)

    def test_confirm_list_empty(self):
        request_data = {
            "hashes": [],
            "target": "jid@example.com"}
        rv = self.client.get("/v1/confirm/", query_string=request_data)
        expect(json.loads(rv.data)["confirmed"]).to.be(False)

    def test_confirm_all_found(self):
        request_data = {
            "hashes": ["hashc6id89ad98ad", "hashc6id89ad99ad", "hashc6id89ad238ad"],
            "target": "jid@example.com"}
        rv = self.client.get("/v1/confirm/", query_string=request_data)
        expect(json.loads(rv.data)["confirmed"]).to.be(True)

    def test_confirm_all_found_one_pending(self):
        request_data = {
            "hashes": ["hashc6id89ad98ad", "hashc6id8PENDING", "hashc6id89ad99ad", "hashc6id89ad238ad"],
            "target": "jid@example.com"}
        rv = self.client.get("/v1/confirm/", query_string=request_data)
        expect(json.loads(rv.data)["confirmed"]).to.be(False)

    def test_confirm_all_found_one_not_found(self):
        request_data = {
            "hashes": ["hashc6id89ad98ad", "NOTFOUND", "hashc6id89ad99ad", "hashc6id89ad238ad"],
            "target": "jid@example.com"}
        rv = self.client.get("/v1/confirm/", query_string=request_data)
        expect(json.loads(rv.data)["confirmed"]).to.be(False)

    def test_confirm_all_found_one_wrong(self):
        request_data = {
            "hashes": ["hashc6id89ad98ad", "hashc6id89ad98a3", "hashc6id89ad99ad", "hashc6id89ad238ad"],
            "target": "jid@example.com"}
        rv = self.client.get("/v1/confirm/", query_string=request_data)
        expect(json.loads(rv.data)["confirmed"]).to.be(False)


    # def test_register(self):
    #     raise NotImplementedError

    # def test_approve(self):
    #     raise NotImplementedError

    # def test_request(self):
    #     raise NotImplementedError

