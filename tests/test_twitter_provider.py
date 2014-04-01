
import test_oauth_provider
from itseme.providers import Twitter


class TestTwitterProvider(test_oauth_provider.TestOAuthProvider):
    provider_class = Twitter