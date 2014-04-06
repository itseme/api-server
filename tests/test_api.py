# -*- encoding: utf-8 -*-
from mock import MagicMock, patch
from sure import expect
from flask import abort, make_response

from itseme.providers import Provider
from itseme import app
from itseme import tasks

import unittest
import json

from _base import BaseTestMixin


class TestV1Api(BaseTestMixin, unittest.TestCase):

    def setUp(self):
        super(TestV1Api, self).setUp()
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
        expect(rv.status_code).to.equal(200)
        expect(json.loads(rv.data)["confirmed"]).to.be(False)

    def test_confirm_all_found(self):
        request_data = {
            "hashes": ["hashc6id89ad98ad", "hashc6id89ad99ad", "hashc6id89ad238ad"],
            "target": "jid@example.com"}
        rv = self.client.get("/v1/confirm/", query_string=request_data)
        expect(rv.status_code).to.equal(200)
        expect(json.loads(rv.data)["confirmed"]).to.be(True)

    def test_confirm_with_json(self):
        request_data = {
            "hashes": ["hashc6id89ad98ad", "hashc6id89ad99ad", "hashc6id89ad238ad"],
            "target": "jid@example.com"}
        rv = self.client.post("/v1/confirm/", data=json.dumps(request_data))
        expect(rv.status_code).to.equal(200)
        expect(json.loads(rv.data)["confirmed"]).to.be(True)

    def test_confirm_too_many(self):
        request_data = {
            "hashes": [str(x) for x in xrange(1001)],
            "target": "jid@example.com"}
        rv = self.client.get("/v1/confirm/", query_string=request_data)
        expect(rv.status_code).to.equal(413)
        expect(json.loads(rv.data)["error"]["code"]).to.equal("too_many_requested")

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

    def test_verify_not_found(self):
        rv = self.client.get("/v1/verify/NOTFOUND")
        expect(rv.status_code).to.equal(404)
        data = json.loads(rv.data)
        expect(data["error"]["code"]).to.equal("not_found")
        expect(data["confirmed"]).to.be(False)

    def test_verify_not_pending(self):
        rv = self.client.get("/v1/verify/hashc6id89ad238ad")
        expect(rv.status_code).to.equal(404)
        data = json.loads(rv.data)
        expect(data["error"]["code"]).to.equal("not_found")
        expect(data["confirmed"]).to.be(False)

    def test_verify(self):
        mock_provider = MagicMock(spec=Provider)
        app.PROVIDERS["provider_two"] = lambda x: mock_provider
        doc = self.database["PENDING_hashc6id8"]

        rv = self.client.get("/v1/verify/hashc6id8")
        expect(rv.status_code).to.equal(200)
        expect(json.loads(rv.data)["confirmed"]).to.be(True)
        expect(self.database).should_not.contain("PENDING_hashc6id8")
        mock_provider.verify.assert_called_once_with(doc)

    def test_verify_already_exists(self):
        mock_provider = MagicMock(spec=Provider)
        app.PROVIDERS["test_provider"] = lambda x: mock_provider
        doc = self.database["PENDING_ALREADY_EXISTS"]

        rv = self.client.get("/v1/verify/ALREADY_EXISTS")
        expect(rv.status_code).to.equal(200)
        expect(json.loads(rv.data)["confirmed"]).to.be(True)
        expect(self.database).should_not.contain("PENDING_ALREADY_EXISTS")
        mock_provider.verify.assert_called_once_with(doc)


    def test_verify_with_message(self):

        mock_provider = MagicMock(spec=Provider)
        mock_provider.verify.return_value = {"we want": "candy"}
        app.PROVIDERS["provider_two"] = lambda x: mock_provider
        doc = self.database["PENDING_hashc6id8"]

        rv = self.client.get("/v1/verify/hashc6id8")
        expect(rv.status_code).to.equal(200)
        expect(json.loads(rv.data)["confirmed"]).to.be(True)
        expect(json.loads(rv.data)["we want"]).to.equal("candy")
        expect(self.database).should_not.contain("PENDING_hashc6id8")
        expect(self.database["hashc6id8"].has_key("provider")).to.be(False)
        mock_provider.verify.assert_called_once_with(doc)


    def test_verify_complaining_provider(self):

        mock_provider = MagicMock(spec=Provider)
        mock_provider.verify.side_effect = lambda x: abort(409)
        app.PROVIDERS["provider_two"] = lambda x: mock_provider

        rv = self.client.get("/v1/verify/hashc6id8")
        expect(rv.status_code).to.equal(409)

    def test_verify_returning_provider(self):

        mock_provider = MagicMock(spec=Provider)
        mock_provider.verify.side_effect = lambda x: make_response(("Test", 303, {}))
        app.PROVIDERS["provider_two"] = lambda x: mock_provider

        rv = self.client.get("/v1/verify/hashc6id8")
        expect(rv.status_code).to.equal(303)

    def test_register_unknown_target(self):
        rv = self.client.get("/v1/register/coolio_service/master_keen/unknown@example.com")
        expect(rv.status_code).to.equal(401)
        data = json.loads(rv.data)
        expect(data["error"]["code"]).to.equal("target_unconfirmed")

    def test_register_unconfirmed(self):
        rv = self.client.get("/v1/register/coolio_service/master_keen/unconfirmed@example.com")
        expect(rv.status_code).to.equal(401)
        data = json.loads(rv.data)
        expect(data["error"]["code"]).to.equal("target_unconfirmed")

    def test_register_complaining_provider(self):
        mock_provider = MagicMock(spec=Provider)
        mock_provider.register.side_effect = lambda x: abort(409)
        app.PROVIDERS["coolio_service"] = lambda x: mock_provider

        rv = self.client.get("/v1/register/coolio_service/master_keen/my_jabber@example.com")
        expect(rv.status_code).to.equal(409)

    def test_register_returning_provider(self):

        mock_provider = MagicMock(spec=Provider)
        mock_provider.register.side_effect = lambda x: make_response(("Test", 303, {}))
        app.PROVIDERS["coolio_service"] = lambda x: mock_provider

        rv = self.client.get("/v1/register/coolio_service/master_keen/my_jabber@example.com")
        expect(rv.status_code).to.equal(303)

    def test_register_new(self):

        mock_provider = MagicMock(spec=Provider)
        mock_provider.register.return_value = {}
        app.PROVIDERS["coolio_service"] = lambda x: mock_provider

        rv = self.client.get("/v1/register/coolio_service/master_keen/my_jabber@example.com")
        expect(rv.status_code).to.equal(200)
        data = json.loads(rv.data)
        expect(data["status"]).to.equal("pending")
        key = data["hash"]
        expect(self.database).should_not.contain(key)
        expect(self.database).to.contain("PENDING_%s" % key)
        db_entry = self.database["PENDING_%s" % key]
        expect(db_entry["provider_id"]).to.equal("master_keen")
        expect(db_entry["provider"]).to.equal("coolio_service")

        mock_provider.register.assert_called_once_with(db_entry)

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
        expect(self.database).should_not.contain(key)
        expect(self.database).to.contain("PENDING_%s" % key)
        db_entry = self.database["PENDING_%s" % key]
        expect(db_entry["provider_id"]).to.equal("diddle")
        expect(db_entry["provider"]).to.equal("coolio_service")
        expect(db_entry["target"]).to.equal("xmpp@example.com")

        mock_provider.register.assert_called_once_with(db_entry)

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

        expect(self.database).should_not.contain(key)
        expect(self.database).to.contain("PENDING_%s" % key)
        db_entry = self.database["PENDING_%s" % key]
        expect(db_entry["provider_id"]).to.equal("tommy diddle")
        expect(db_entry["provider"]).to.equal("space")
        expect(db_entry["target"]).to.equal("my_jab er@example.com")

        mock_provider.register.assert_called_once_with(db_entry)

    def test_registered_twice(self):

        mock_provider = MagicMock(spec=Provider)
        mock_provider.register.side_effect = ValueError()
        app.PROVIDERS["email"] = lambda x: mock_provider

        rv = self.client.get("/v1/register/email/home@example.com/xmpp@example.com")
        expect(rv.status_code).to.equal(200)
        data = json.loads(rv.data)
        expect(data["status"]).to.equal("pending")
        key = data["hash"]

        expect(self.database).should_not.contain(key)
        expect(self.database).to.contain("PENDING_%s" % key)
        db_entry = self.database["PENDING_%s" % key]
        # make sure it hasn't been touched
        expect(db_entry["email"]).to.equal("home@example.com")
        expect(db_entry["target"]).to.equal("xmpp@example.com")

        expect(mock_provider.register.called).should.be(False)

    def test_registered_twice_explicit_redo(self):

        mock_provider = MagicMock(spec=Provider)
        mock_provider.register.return_value = {"sms": "send"}
        app.PROVIDERS["email"] = lambda x: mock_provider

        # already registered, but asked to resend
        rv = self.client.get("/v1/register/email/home@example.com/xmpp@example.com?resend=1")
        expect(rv.status_code).to.equal(200)
        data = json.loads(rv.data)
        expect(data["status"]).to.equal("pending")
        expect(data["sms"]).to.equal("send")
        key = data["hash"]

        expect(self.database).should_not.contain(key)
        expect(self.database).to.contain("PENDING_%s" % key)
        db_entry = self.database["PENDING_%s" % key]

        # shouldn't have been touched, aside from the increase in retries
        expect(db_entry).should_not.contain("provider_id")
        expect(db_entry["retries"]).to.equal(1)
        expect(db_entry["email"]).to.equal("home@example.com")
        expect(db_entry["target"]).to.equal("xmpp@example.com")

        mock_provider.register.assert_called_once_with(db_entry)

    def test_registered_overwrite(self):

        mock_provider = MagicMock(spec=Provider)
        mock_provider.register.return_value = {"sms": "send"}
        app.PROVIDERS["email"] = lambda x: mock_provider

        rv = self.client.get("/v1/register/email/home@example.com/my_jabber@example.com")
        expect(rv.status_code).to.equal(200)
        data = json.loads(rv.data)
        expect(data["status"]).to.equal("pending")
        expect(data["sms"]).to.equal("send")
        key = data["hash"]

        expect(self.database).should_not.contain(key)
        expect(self.database).to.contain("PENDING_%s" % key)
        db_entry = self.database["PENDING_%s" % key]
        expect(db_entry["target"]).to.equal("my_jabber@example.com")

        mock_provider.register.assert_called_once_with(db_entry)

    def test_register_self_verify_xmpp(self):

        mock_provider = MagicMock(spec=Provider)
        mock_provider.register.return_value = {"xmpp": "message is out"}
        app.PROVIDERS["xmpp"] = lambda x: mock_provider

        rv = self.client.get("/v1/register/xmpp/new_other@example.com/new_other@example.com")
        expect(rv.status_code).to.equal(200)
        data = json.loads(rv.data)
        expect(data["status"]).to.equal("pending")
        expect(data["xmpp"]).to.equal("message is out")

        key = data["hash"]
        expect(self.database).should_not.contain(key)
        expect(self.database).to.contain("PENDING_%s" % key)
        db_entry = self.database["PENDING_%s" % key]

        expect(db_entry["provider_id"]).to.equal("new_other@example.com")
        expect(db_entry["provider"]).to.equal("xmpp")
        expect(db_entry["target"]).to.equal("new_other@example.com")

        mock_provider.register.assert_called_once_with(db_entry)

    def test_contact_unknown_target(self):
        # totaly unknown to the DB
        json_data = {
            "target": "unknown@example.com",
            "contact_info": [{
                "provider": "",
                "id": ""}],
            "contacts": ["hash", "hash"]
        }
        rv = self.client.post("/v1/contact/", data=json.dumps(json_data))
        expect(rv.status_code).to.equal(400)
        data = json.loads(rv.data)
        expect(data["error"]["code"]).to.equal("target_unconfirmed")

        # not yet confirmed
        json_data["target"] = "unconfirmed@example.com"
        rv = self.client.post("/v1/contact/", data=json.dumps(json_data))
        expect(rv.status_code).to.equal(400)
        data = json.loads(rv.data)
        expect(data["error"]["code"]).to.equal("target_unconfirmed")

    def test_contact_broken_data(self):
        rv = self.client.post("/v1/contact/")
        expect(rv.status_code).to.equal(400)
        data = json.loads(rv.data)
        expect(data["error"]["code"]).to.equal("json_decode_error")

        rv = self.client.post("/v1/contact/", data="String:Something")
        expect(rv.status_code).to.equal(400)
        data = json.loads(rv.data)
        expect(data["error"]["code"]).to.equal("json_decode_error")

    def test_contact_incomplete(self):
        json_data = {
            "target": " ",
            "contact_info": [],
            "contacts": []
        }

        rv = self.client.post("/v1/contact/", data=json.dumps(json_data))
        data = json.loads(rv.data)
        expect(rv.status_code).to.equal(400)
        expect(data["error"]["code"]).to.equal("value_error")
        expect(data["error"]["message"]).to.contain("target")

        json_data["target"] = "unconfirmed@example.com"

        rv = self.client.post("/v1/contact/", data=json.dumps(json_data))
        data = json.loads(rv.data)
        expect(rv.status_code).to.equal(400)
        expect(data["error"]["code"]).to.equal("value_error")
        expect(data["error"]["message"]).to.contain("contact_info")

        json_data["contact_info"] = ["a", "b"]
        rv = self.client.post("/v1/contact/", data=json.dumps(json_data))
        data = json.loads(rv.data)
        expect(rv.status_code).to.equal(400)
        expect(data["error"]["code"]).to.equal("value_error")
        expect(data["error"]["message"]).to.contain("contacts")

        json_data.pop("contact_info")
        rv = self.client.post("/v1/contact/", data=json.dumps(json_data))
        data = json.loads(rv.data)
        expect(rv.status_code).to.equal(400)
        expect(data["error"]["code"]).to.equal("key_error")
        expect(data["error"]["message"]).to.contain("contacts")

    def test_contact_target_unconfirmed(self):
        json_data = {
            "target": "unconfirmed@example.com",
            "contact_info": ["a", "b"],
            "contacts": ["hash", "hash"]
        }

        rv = self.client.post("/v1/contact/", data=json.dumps(json_data))
        data = json.loads(rv.data)
        expect(rv.status_code).to.equal(400)
        expect(data["error"]["code"]).to.equal("target_unconfirmed")

    def test_contact_too_many(self):
        json_data = {
            "target": "unconfirmed@example.com",
            "contact_info": ["a", "b"],
            "contacts": [str(x) for x in xrange(1001)]
        }

        rv = self.client.post("/v1/contact/", data=json.dumps(json_data))
        expect(rv.status_code).to.equal(413)
        expect(json.loads(rv.data)["error"]["code"]
              ).to.equal("too_many_requested")

    def test_contact_faulty_contact_info(self):
        json_data = {
            "target": "xmpp@example.com",
            "contact_info": ["a", "b"],
            "contacts": ["hash", "hash"]
        }

        rv = self.client.post("/v1/contact/", data=json.dumps(json_data))
        data = json.loads(rv.data)
        expect(rv.status_code).to.equal(400)
        expect(data["error"]["code"]).to.equal("insufficient_contact_info")

        json_data = {
            "target": "xmpp@example.com",
            "contact_info": [
                {"protocol": "facebook", "id": "abdc"},
                {"protocol": "twitter", "id": "abracadabra"},
                {"protocol": "phone", "id": "+4912345"},
                # none can be confirmed unfortunately
                {}, # this one is broken
                None # and so is this.
                ],
            "contacts": ["hash", "hash"]
        }

        rv = self.client.post("/v1/contact/", data=json.dumps(json_data))
        data = json.loads(rv.data)
        expect(rv.status_code).to.equal(400)
        expect(data["error"]["code"]).to.equal("insufficient_contact_info")


        json_data = {
            "target": "xmpp@example.com",
            "contact_info": [
                # existing but not mine
                {"protocol": "phone", "id": "+0011346648"},
                # none can be confirmed unfortunately
                {}, # this one is broken
                None # and so is this.
                ],
            "contacts": ["hash", "hash"]
        }

        rv = self.client.post("/v1/contact/", data=json.dumps(json_data))
        data = json.loads(rv.data)
        expect(rv.status_code).to.equal(400)
        expect(data["error"]["code"]).to.equal("insufficient_contact_info")

    def test_contact_faulty_hashes_still_replies(self):
        json_data = {
            "target": "xmpp@example.com",
            "contact_info": [
                {"protocol": "phone", "id": "+00112345678"},
                {"protocol": "email", "id": "hunter@jobs.com"},
                {"protocol": "phone", "id": "+4912345"},
                {}, # this one is broken
                None # and so is this.
                ],
            "contacts": ["hash", "hash"]
        }

        with patch.object(tasks.contact_request, "delay") as mocked_task:
            rv = self.client.post("/v1/contact/", data=json.dumps(json_data))
            # though it hasn't been called!
            expect(mocked_task.call_list).should.have.length_of(0)

        expect(rv.status_code).to.equal(200)
        data = json.loads(rv.data)
        expect(data["status"]).to.equal("requests_send")


    @patch("itseme.tasks.SendMsgBot", spec=tasks.SendMsgBot)
    def test_register(self, send_mock):
        json_data = {
            "target": "xmpp@example.com",
            "contact_info": [
                {"protocol": "phone", "id": "+00112345678"},
                {"protocol": "email", "id": "hunter@jobs.com"},
                {"protocol": "phone", "id": "+4912345"},
                {}, # this one is broken
                None # and so is this.
                ],
            "contacts": [
                # not existant:
                "hash",
                # goes to: my_jabber@example.com
                "397ee3ee893ba686b8f228078803ce34911b35c8bf15a7986310de1225589fe13706a3242376da92c144a0e38e4693ac237840879947dc984870715c08793909",
                # and twice "jid@example.com", but should only be send once:
                "hashc6id89ad99ad",
                "hashc6id89ad238ad",
                # still pending: not send:
                "e5d20f91694fde312aeb9e784178c8bd8a386d8c2789dfed7dc14a35fb8ea88fd0a1583a0a98b80058e8c9e6d7c8acd2f8c7ab240709600854f7e0bdabbc7078",
                # self: - should be filtered out
                "abce880ed2d448abffa8efa8939d8e15625ad16ff2330d97388f32fee480d799b9753e1d2f362c7deb1f7ea83bfbbf234712f9b45979496589812d0016e2cb48"
                ]
        }

        send_mock.return_value = send_mock
        send_mock.connect.return_value = True

        rv = self.client.post("/v1/contact/", data=json.dumps(json_data))

        # return values
        expect(rv.status_code).to.equal(200)
        data = json.loads(rv.data)
        expect(data["status"]).to.equal("requests_send")

        # checking message information

        send_mock.connect.assert_called_once()
        send_mock.process.assert_called_once_with(block=True)

        message = send_mock.call_args[0][3]

        expect(type(message)).to.be(dict)
        expect(message["contact"]["jid"]).should.be.a(basestring)
        expect(message["contact"]["info"]).should.be.a(basestring)
        info = json.loads(message["contact"]["info"])
        expect(info).to.equal([
                {'confirmed': True, "protocol": "phone", "id": "+00112345678"},
                {'confirmed': True, "protocol": "email", "id": "hunter@jobs.com"},
                ])

        expect(message["contact"]["jid"]).to.equal("xmpp@example.com")

        # checking recipients:
        recipients = send_mock.call_args[0][2]
        expect(recipients).to.equal(["my_jabber@example.com", "jid@example.com"])

