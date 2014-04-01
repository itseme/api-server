
import test_oauth_provider
from itseme.providers import Facebook

from mock import patch
from sure import expect

RETURN_VALUE = {"username": "themattharris", "id": "1443XXX87X"}

class TestFacebookProvider(test_oauth_provider.TestOAuthProvider):
    provider_class = Facebook


    def test_confirm_user_matches(self):
        doc = {"provider_id": "themattharris"}
        with patch.object(self.remote, "get") as getter:
            getter.return_value = RETURN_VALUE
            resp = self.provider.confirm(doc, "something")\

            expect(resp).to.be(True)
            getter.assert_called_once_with("me?fields=username")

    def test_confirm_user_doesnt_match(self):
        doc = {"provider_id": "octocat"}
        with patch.object(self.remote, "get") as getter:
            getter.return_value = RETURN_VALUE
            resp = self.provider.confirm(doc, "something")\

            expect(resp).to.be(False)
            getter.assert_called_once_with("me?fields=username")