
from itseme.providers import OAuthProvider, OAuthRemoteApp
from itseme.app import app

from mock import MagicMock
from flask import session, redirect

from sure import expect
import unittest

class SubProv(OAuthProvider):
    name = "sub_prov"
    config = {"app_key": "YOLO"}


class TestOAuthProvider(unittest.TestCase):

    provider_class = SubProv

    def setUp(self):
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
        self.remote.authorize.assert_called_once()

    def test_register_environ_with_next(self):
        self.remote.authorize.return_value = redirect("http://home.example.com/something?8=a")
        doc = {"provider_id": "test_id", "_id": "HASHIKU"}

        with app.test_request_context('/?name=Peter&next=whatever.com'):
            session[self.provider.key] = ["a", "b"]
            resp = self.provider.register(doc)

        expect(resp["goto"]).to.equal("http://home.example.com/something?8=a")
        expect(doc[self.provider.key]).to.equal(["a", "b"])
        self.remote.authorize.assert_called_once() # we aren't really checking wether next arrived here ..

