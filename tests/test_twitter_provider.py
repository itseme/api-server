
import test_oauth_provider
from itseme.providers import Twitter

from mock import patch
from sure import expect

RETURN_VALUE = {"screen_name": "Matt Harris",
                "profile_sidebar_border_color": "C0DEED",
                "profile_background_tile": False,
                "profile_sidebar_fill_color": "DDEEF6",
                "location": "San Francisco",
                "profile_image_url": "http://a1.twimg.com/profile_images/554181350/matt_normal.jpg",
                "created_at": "Sat Feb 17 20:49:54 +0000 2007",
                "profile_link_color": "0084B4",
                "favourites_count": 95,
                "url": "http://themattharris.com",
                "contributors_enabled": False,
                "utc_offset": -28800,
                "id": 777925,
                "profile_use_background_image": True,
                "profile_text_color": "333333",
                "protected": False,
                "followers_count": 1025,
                "lang": "en",
                "verified": False,
                "profile_background_color": "C0DEED",
                "geo_enabled": True,
                "notifications": False,
                "description": "Developer Advocate at Twitter. Also a hacker and British expat who is married to @cindyli and lives in San Francisco.",
                "time_zone": "Tijuana",
                "friends_count": 294,
                "statuses_count": 2924,
                "profile_background_image_url": "http://s.twimg.com/a/1276711174/images/themes/theme1/bg.png",
                "screen_name": "themattharris",
                "following": False
    }


class TestTwitterProvider(test_oauth_provider.TestOAuthProvider):
    provider_class = Twitter

    def test_confirm_user_matches(self):
        doc = {"provider_id": "themattharris"}
        resp = self.provider.confirm(doc, RETURN_VALUE)

        expect(resp).to.be(True)

    def test_confirm_user_doesnt_match(self):
        doc = {"provider_id": "octocat"}
        resp = self.provider.confirm(doc, RETURN_VALUE)

        expect(resp).to.be(False)
