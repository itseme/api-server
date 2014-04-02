
from itseme.providers import XmppProvider
from itseme.xmpp_client import SendMsgBot
from itseme.app import app


from mock import MagicMock, patch
from flask import session, redirect

from sure import expect
from _base import BaseTestMixin
import unittest
import json


class TestXmppProvider(BaseTestMixin, unittest.TestCase):

    def setUp(self):
        super(TestXmppProvider, self).setUp()
        self.provider = XmppProvider(app)

    def test_verify(self):
        doc = {"provider_id" : "nope", "provider": "xmpp", "xmpp_code": "4758"}
        with app.test_request_context('/?code=4758'):
            resp = self.provider.verify(doc)

        expect(resp).to.be.none
        expect(doc["status"]).to.equal("confirmed")

    def test_verify_no_code(self):
        doc = {"provider_id" : "nope", "status": "args", "xmpp_code": "4758"}
        with app.test_request_context('/?codeR=4758'):
            resp = self.provider.verify(doc)

        expect(resp.status_code).to.equal(400)
        expect(json.loads(resp.data)["error"]["code"]).to.equal("missing_code")
        expect(doc["status"]).to.equal("args")

    def test_verify_faulty_code(self):
        doc = {"provider_id" : "nope", "status": "args", "xmpp_code": "4758"}
        with app.test_request_context('/?code=47x58'):
            resp = self.provider.verify(doc)

        expect(resp.status_code).to.equal(400)
        expect(json.loads(resp.data)["error"]["code"]).to.equal("faulty_code")
        expect(doc["status"]).to.equal("args")

    @patch("itseme.tasks.SendMsgBot", spec=SendMsgBot)
    def test_register(self, send_mock):
        doc = {"_id": "hashipu", "provider_id": "nope", "status": "args"}
        send_mock.return_value = send_mock
        send_mock.connect.return_value = True
        self.provider.register(doc)

        expect(doc["xmpp_code"]).should.have.length_of(4)

        message = send_mock.call_args[0][3]
        expect(message).should.be.a(dict)
        expect(message["verify"]["code"]).should.be.a(basestring)
        code = message["verify"]["code"]
        expect(code).to.equal(doc["xmpp_code"])
        expect(message["text"]).to.contain(code)
        expect(message["verify"]["hash"]).to.equal("hashipu")
        send_mock.connect.assert_called_once()
        send_mock.process.assert_called_once_with(block=True)

