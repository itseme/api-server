# -*- encoding: utf-8 -*-
from mock import MagicMock
from sure import expect
from providers import Provider
from flask import abort

import unittest
import json
import app
import yaml


class TestV1Api(unittest.TestCase):

    def setUp(self):
        self.database = yaml.load(open("test_data.yml"))
        app.app.config.from_object("config.TestConfig")
        app._get_db = lambda: self.database

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

    def test_confirm_too_many(self):
        request_data = {
            "hashes": [str(x) for x in xrange(101)],
            "target": "jid@example.com"}
        rv = self.client.get("/v1/confirm/", query_string=request_data)
        expect(rv.status_code).to.equal(400)

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

    def test_approve_not_found(self):
        rv = self.client.get("/v1/approve/NOTFOUND")
        expect(rv.status_code).to.equal(404)
        data = json.loads(rv.data)
        expect(data["error"]["code"]).to.equal("not_found")
        expect(data["confirmed"]).to.be(False)

    def test_approve_not_pending(self):
        rv = self.client.get("/v1/approve/hashc6id89ad238ad")
        expect(rv.status_code).to.equal(403)
        data = json.loads(rv.data)
        expect(data["error"]["code"]).to.equal("not_pending")
        expect(data["confirmed"]).to.be(False)

    def test_approve(self):

        mock_provider = MagicMock(spec=Provider)
        app.PROVIDERS["provider_two"] = lambda x: mock_provider

        rv = self.client.get("/v1/approve/hashc6id8PENDING")
        expect(rv.status_code).to.equal(200)
        expect(json.loads(rv.data)["confirmed"]).to.be(True)
        expect(self.database["hashc6id8PENDING"]["confirmed"]).to.be(True)
        mock_provider.approve.assert_called_once_with(self.database["hashc6id8PENDING"])

    def test_approve_with_message(self):

        mock_provider = MagicMock(spec=Provider)
        mock_provider.approve.return_value = {"we want": "candy"}
        app.PROVIDERS["provider_two"] = lambda x: mock_provider

        rv = self.client.get("/v1/approve/hashc6id8PENDING")
        expect(rv.status_code).to.equal(200)
        expect(json.loads(rv.data)["confirmed"]).to.be(True)
        expect(json.loads(rv.data)["we want"]).to.equal("candy")
        expect(self.database["hashc6id8PENDING"]["confirmed"]).to.be(True)
        mock_provider.approve.assert_called_once_with(self.database["hashc6id8PENDING"])


    def test_approve_complaining_provider(self):

        mock_provider = MagicMock(spec=Provider)
        mock_provider.approve.side_effect = lambda x: abort(409)
        app.PROVIDERS["provider_two"] = lambda x: mock_provider

        rv = self.client.get("/v1/approve/hashc6id8PENDING")
        expect(rv.status_code).to.equal(409)


    def test_register_unknown_target(self):
        rv = self.client.get("/v1/register/coolio_service/master_keen/unknown@example.com")
        expect(rv.status_code).to.equal(401)

    def test_register_unconfirmed(self):
        rv = self.client.get("/v1/register/coolio_service/master_keen/unconfirmed@example.com")
        expect(rv.status_code).to.equal(401)

    def test_register_new(self):

        mock_provider = MagicMock(spec=Provider)
        mock_provider.register.return_value = {}
        app.PROVIDERS["coolio_service"] = lambda x: mock_provider

        rv = self.client.get("/v1/register/coolio_service/master_keen/my_jabber@example.com")
        expect(rv.status_code).to.equal(200)
        data = json.loads(rv.data)
        expect(data["status"]).to.equal("pending")
        key = data["hash"]
        db_entry = self.database[key]
        expect(db_entry["provider_id"]).to.equal("master_keen")
        expect(db_entry["provider"]).to.equal("coolio_service")

        mock_provider.register.assert_called_once_with(self.database[key])

    def test_register_new_extended_provider(self):

        mock_provider = MagicMock(spec=Provider)
        mock_provider.register.return_value = {"goto": "/home"}
        app.PROVIDERS["coolio_service"] = lambda x: mock_provider

        rv = self.client.get("/v1/register/coolio_service/diddle/xmpp@example.com")
        expect(rv.status_code).to.equal(200)
        data = json.loads(rv.data)
        expect(data["status"]).to.equal("pending")
        expect(data["goto"]).to.equal("/home")

        key = data["hash"]
        db_entry = self.database[key]
        expect(db_entry["provider_id"]).to.equal("diddle")
        expect(db_entry["provider"]).to.equal("coolio_service")
        expect(db_entry["target"]).to.equal("xmpp@example.com")

        mock_provider.register.assert_called_once_with(self.database[key])

    def test_register_space_in_name(self):

        mock_provider = MagicMock(spec=Provider)
        mock_provider.register.return_value = {"sms": "send"}
        app.PROVIDERS["space"] = lambda x: mock_provider

        rv = self.client.get("/v1/register/space/tommy diddle/my_jab er@example.com")
        expect(rv.status_code).to.equal(200)
        data = json.loads(rv.data)
        expect(data["status"]).to.equal("pending")
        expect(data["sms"]).to.equal("send")
        key = data["hash"]

        db_entry = self.database[key]
        expect(db_entry["provider_id"]).to.equal("tommy diddle")
        expect(db_entry["provider"]).to.equal("space")
        expect(db_entry["target"]).to.equal("my_jab er@example.com")

        mock_provider.register.assert_called_once_with(self.database[key])

