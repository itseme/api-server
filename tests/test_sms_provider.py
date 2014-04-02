
from itseme.providers import SmsProvider
from itseme.app import app
from itseme import tasks

from mock import MagicMock, patch

from sure import expect
from _base import BaseTestMixin
import unittest
import json


class TestSmsProvider(BaseTestMixin, unittest.TestCase):

    def setUp(self):
        super(TestSmsProvider, self).setUp()
        self.provider = SmsProvider(app)

    def test_verify(self):
        doc = {"provider_id" : "nope", "provider": "phone", "phone_code": "4758"}
        with app.test_request_context('/?code=4758'):
            resp = self.provider.verify(doc)

        expect(resp).to.be.none
        expect(doc["status"]).to.equal("confirmed")

    def test_verify_no_code(self):
        doc = {"provider_id" : "nope", "status": "args", "phone_code": "4758"}
        with app.test_request_context('/?codeR=4758'):
            resp = self.provider.verify(doc)

        expect(resp.status_code).to.equal(400)
        expect(json.loads(resp.data)["error"]["code"]).to.equal("missing_code")
        expect(doc["status"]).to.equal("args")

    def test_verify_faulty_code(self):
        doc = {"provider_id" : "nope", "status": "args", "phone_code": "4758"}
        with app.test_request_context('/?code=47x58'):
            resp = self.provider.verify(doc)

        expect(resp.status_code).to.equal(400)
        expect(json.loads(resp.data)["error"]["code"]).to.equal("faulty_code")
        expect(doc["status"]).to.equal("args")

    @patch("itseme.tasks.TwilioRestClient", spec=tasks.TwilioRestClient)
    def test_register(self, twilio_client):
        doc = {"_id": "HASHCODE", "provider_id": "+123456789",
               "provider": "phone", "status": "args",
               "target": "ben@jabber.com"}

        twilio_client.return_value = twilio_client
        twilio_client.messages = MagicMock()
        twilio_client.messages.create = message_creator = MagicMock()
        self.provider.register(doc)

        expect(doc["phone_code"]).should.have.length_of(4)

        message_creator.assert_called_once()
        args = message_creator.call_args[1]
        expect(args["to"]).to.equal("+123456789")
        expect(args["body"]).to.contain(doc["phone_code"])
        expect(args["body"]).to.contain(doc["target"])


    @patch("itseme.tasks.TwilioRestClient", spec=tasks.TwilioRestClient)
    def test_register_with_from(self, twilio_client):
        tasks.celery.conf.update(TWILIO_FROM="+55678")
        doc = {"_id": "HASHCODE", "provider_id": "+123423as89",
               "provider": "phone", "status": "args",
               "target": "xmpp@example.com"}

        twilio_client.return_value = twilio_client
        twilio_client.messages = MagicMock()
        twilio_client.messages.create = message_creator = MagicMock()
        self.provider.register(doc)

        expect(doc["phone_code"]).should.have.length_of(4)

        message_creator.assert_called_once()
        args = message_creator.call_args[1]
        expect(args["to"]).to.equal("+123423as89")
        expect(args["body"]).to.contain(doc["phone_code"])
        expect(args["body"]).to.contain(doc["target"])
        expect(args["from_"]).to.equal("+55678") # SHORTNUM
