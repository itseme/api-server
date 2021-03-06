
import test_oauth_provider
from itseme.providers import Github

from mock import patch, Mock
from sure import expect

# AS COLLECTED FROM https://developer.github.com/v3/users/#get-the-authenticated-user
RETURN_VALUE = {"login": "octocat",
                "id": 1,
                "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                "gravatar_id": "somehexcode",
                "url": "https://api.github.com/users/octocat",
                "html_url": "https://github.com/octocat",
                "followers_url": "https://api.github.com/users/octocat/followers",
                "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                "organizations_url": "https://api.github.com/users/octocat/orgs",
                "repos_url": "https://api.github.com/users/octocat/repos",
                "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                "received_events_url": "https://api.github.com/users/octocat/received_events",
                "type": "User",
                "site_admin": False,
                "name": "monalisa octocat",
                "company": "GitHub",
                "blog": "https://github.com/blog",
                "location": "San Francisco",
                "email": "octocat@github.com",
                "hireable": False,
                "bio": "There once was...",
                "public_repos": 2,
                "public_gists": 1,
                "followers": 20,
                "following": 0,
                "created_at": "2008-01-14T04:33:35Z",
                "updated_at": "2008-01-14T04:33:35Z",
                "total_private_repos": 100,
                "owned_private_repos": 100,
                "private_gists": 81,
                "disk_usage": 10000,
                "collaborators": 8,
                "plan": {
                    "name": "Medium",
                    "space": 400,
                    "collaborators": 10,
                    "private_repos": 20
                    }
                }


class TestGithubProvider(test_oauth_provider.TestOAuthProvider):
    provider_class = Github

    def test_confirm_user_matches(self):
        doc = {"provider_id": "octocat"}
        v = Mock()
        v.data = RETURN_VALUE
        with patch.object(self.remote, "get") as getter:
            getter.return_value = v
            resp = self.provider.confirm(doc, "something")\

            expect(resp).to.be(True)
            getter.assert_called_once_with("user")

    def test_confirm_user_doesnt_match(self):
        doc = {"provider_id": "octocat_is_not"}
        v = Mock()
        v.data = RETURN_VALUE
        with patch.object(self.remote, "get") as getter:
            getter.return_value = v
            resp = self.provider.confirm(doc, "something")\

            expect(resp).to.be(False)
            getter.assert_called_once_with("user")
