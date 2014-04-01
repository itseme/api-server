
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

    def test_approve(self):
        doc = {"provider_id" : "nope", "provider": "xmpp", "xmpp_code": "4758"}
        with app.test_request_context('/?code=4758'):
            resp = self.provider.approve(doc)

        expect(resp).to.be(None)
        expect(doc["status"]).to.equal("confirmed")

    def test_approve_no_code(self):
        doc = {"provider_id" : "nope", "status": "args", "xmpp_code": "4758"}
        with app.test_request_context('/?codeR=4758'):
            resp = self.provider.approve(doc)

        expect(resp.status_code).to.equal(400)
        expect(json.loads(resp.data)["error"]["code"]).to.equal("missing_code")
        expect(doc["status"]).to.equal("args")

    def test_approve_faulty_code(self):
        doc = {"provider_id" : "nope", "status": "args", "xmpp_code": "4758"}
        with app.test_request_context('/?code=47x58'):
            resp = self.provider.approve(doc)

        expect(resp.status_code).to.equal(400)
        expect(json.loads(resp.data)["error"]["code"]).to.equal("faulty_code")
        expect(doc["status"]).to.equal("args")

    @patch.object(SendMsgBot, "process")
    @patch.object(SendMsgBot, "connect")
    def test_register(self, mock_connect, mock_process):
        doc = {"provider_id" : "nope", "status": "args",}
        mock_connect.return_value = True
        self.provider.register(doc)

        mock_connect.assert_called_once()
        mock_process.assert_called_once_with(block=True)
        expect(len(doc["xmpp_code"])).to.equal(4)

