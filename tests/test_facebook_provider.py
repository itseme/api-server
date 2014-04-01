
import test_oauth_provider
from itseme.providers import Facebook


class TestFacebookProvider(test_oauth_provider.TestOAuthProvider):
    provider_class = Facebook