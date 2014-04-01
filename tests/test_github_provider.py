
import test_oauth_provider
from itseme.providers import Github


class TestGithubProvider(test_oauth_provider.TestOAuthProvider):
    provider_class = Github