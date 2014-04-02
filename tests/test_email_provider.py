
from itseme.providers import EmailProvider
from itseme.app import app
from itseme.app import mail

from mock import MagicMock, patch
from flask import session, redirect

from sure import expect
from _base import BaseTestMixin
import unittest
import json


class TestEmailProvider(BaseTestMixin, unittest.TestCase):

    def setUp(self):
        super(TestEmailProvider, self).setUp()
        self.provider = EmailProvider(app)

    def test_verify(self):
        doc = {"provider_id": "nope", "provider": "email",
               "email_code": "189839"}
        with app.test_request_context('/?code=189839'):
            resp = self.provider.verify(doc)

        expect(resp).should.be.none
        expect(doc["status"]).to.equal("confirmed")

    def test_verify_no_code(self):
        doc = {"provider_id": "nope", "status": "args",
               "email_code": "189839"}
        with app.test_request_context('/?codeR=189839'):
            resp = self.provider.verify(doc)

        expect(resp.status_code).to.equal(400)
        expect(json.loads(resp.data)["error"]["code"]).to.equal("missing_code")
        expect(doc["status"]).to.equal("args")

    def test_verify_faulty_code(self):
        doc = {"provider_id": "nope", "status": "args",
               "email_code": "4758"}
        with app.test_request_context('/?code=18x839'):
            resp = self.provider.verify(doc)

        expect(resp.status_code).to.equal(400)
        expect(json.loads(resp.data)["error"]["code"]).to.equal("faulty_code")
        expect(doc["status"]).to.equal("args")

    def test_register(self):
        doc = {"provider_id": "x@example.com",
               "status": "pending", "_id": "hashcode"}

        with mail.record_messages() as outbox:
            with app.test_request_context('/'):
                self.provider.register(doc)

            expect(doc["email_code"]).should.have.length_of(6)
            expect(outbox).should.have.length_of(1)
            message = outbox[0]
            code = doc["email_code"]
            expect(message.subject).to.contain(code)
            expect(message.body).to.contain(code)
            expect(message.html).to.contain(code)
            expect(message.body).to.contain("hashcode")
            expect(message.html).to.contain("hashcode")


