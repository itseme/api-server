
from itseme.providers import OAuthProvider, OAuthRemoteApp
from itseme.app import app

from mock import MagicMock, patch
from flask import session, redirect

from sure import expect
from _base import BaseTestMixin
import unittest
import json


class SubProv(OAuthProvider):
    name = "sub_prov"
    config = {"app_key": "YOLO"}


class TestOAuthProvider(BaseTestMixin, unittest.TestCase):

    provider_class = SubProv

    def setUp(self):
        super(TestOAuthProvider, self).setUp()
        self.remote = MagicMock(OAuthRemoteApp)
        self.provider = self.provider_class(self)
        self.provider.remote = self.remote

    def test_register_environ(self):
        self.remote.authorize.return_value = redirect("http://home.example.com/something?8=a")
        doc = {"provider_id": "test_id", "_id": "HASHIKU"}

        with app.test_request_context('/?name=Peter'):
            resp = self.provider.register(doc)

        expect(resp["goto"]).to.equal("http://home.example.com/something?8=a")
        expect(doc.get(self.provider.key, "X")).to.equal("X")
        self.remote.authorize.assert_called_once_with(callback=None)

    def test_register_environ_with_next(self):
        self.remote.authorize.return_value = redirect("http://home.example.com/something?8=a")
        doc = {"provider_id": "test_id", "_id": "HASHIKU"}

        with app.test_request_context('/?name=Peter&next=whatever.com'):
            session[self.provider.key] = ["a", "b"]
            resp = self.provider.register(doc)

        expect(resp["goto"]).to.equal("http://home.example.com/something?8=a")
        expect(doc[self.provider.key]).to.equal(["a", "b"])
        self.remote.authorize.assert_called_once()
        expect(self.remote.authorize.call_args[0]).to.contain("next=whatever.com")

    def test_verify_with_code_environ(self):
        self.remote.handle_oauth2_response.return_value = {"a": "b"}
        doc = {"provider_id": "test_id", "_id": "HASHIKU"}

        with patch.object(self.provider, "confirm") as confirm:
            confirm.return_value = True
            with app.test_request_context('/?code=Peter'):
                resp = self.provider.verify(doc)

            confirm.assert_called_once_with(doc, {"a": "b"})
            expect(resp).to.be.none
            expect(doc["status"]).to.equal("confirmed")
            self.remote.handle_oauth2_response.assert_called_once_with()

    def test_verify_with_code_confirm_declines_environ(self):
        self.remote.handle_oauth2_response.return_value = {"a": "b"}
        doc = {"provider_id": "test_id", "_id": "HASHIKU"}

        with patch.object(self.provider, "confirm") as confirm:
            confirm.return_value = False
            with app.test_request_context('/?code=Peter'):
                resp = self.provider.verify(doc)

            confirm.assert_called_once_with(doc, {"a": "b"})
            expect(resp.status_code).to.equal(400)
            data = json.loads(resp.data)
            expect(data["error"]["code"]).to.equal("wrong_user")
            self.remote.handle_oauth2_response.assert_called_once_with()

    def test_verify_with_oauth_verify_environ(self):
        self.remote.handle_oauth1_response.return_value = "YES, MAM!"
        doc = {"provider_id": "test_id", "_id": "HASHIKU"}

        with patch.object(self.provider, "confirm") as confirm:
            confirm.return_value = True
            with app.test_request_context('/?oauth_verifier=Peter'):
                resp = self.provider.verify(doc)

            confirm.assert_called_once_with(doc, "YES, MAM!")
            expect(resp).to.be.none
            expect(doc["status"]).to.equal("confirmed")
            self.remote.handle_oauth1_response.assert_called_once_with()

    def test_verify_with_oauth_verify_confirm_declines_environ(self):
        self.remote.handle_oauth1_response.return_value = "YES, MAM!"
        doc = {"provider_id": "test_id", "_id": "HASHIKU"}

        with patch.object(self.provider, "confirm") as confirm:
            confirm.return_value = False
            with app.test_request_context('/?oauth_verifier=Peter'):
                resp = self.provider.verify(doc)

            confirm.assert_called_once_with(doc, "YES, MAM!")
            expect(resp.status_code).to.equal(400)
            data = json.loads(resp.data)
            expect(data["error"]["code"]).to.equal("wrong_user")
            self.remote.handle_oauth1_response.assert_called_once_with()


    def test_verify_without_codes_environ(self):
        doc = {"provider_id": "test_id", "_id": "HASHIKU"}

        with app.test_request_context('/'):
            resp = self.provider.verify(doc)

        expect(resp.status_code).to.equal(400)
        data = json.loads(resp.data)
        expect(data["error"]["code"]).to.equal("missing_code")


