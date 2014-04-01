from flask_oauthlib.client import OAuth
from flask import session, url_for


class Provider(object):
    def register(self, doc, id, endpoint):
        pass
    def approve(self, doc, hash, confirmcode):
        pass


class OAuthProvider(Provider):

    name = ""
    config = {}

    def __init__(self, app):
        self.app = app
        self.remote = OAuthRemoteApp(self, self.name, **self.config)
        self.remote.tokengetter(self.tokengetter)
        self.key = '%s_oauthtok' % self.name

    def register(self, doc):
        resp = self.remote.authorize(callback=url_for('oauth_authorized',
                                     hashkey=doc["_id"],
                                     next=request.args.get('next') or None))

        if self.key in session:
            doc[self.key] = session.pop(self.key)

        return {"goto": resp.headers['Location']}

    def approve(self, doc):
        if self.key in doc:
            session[self.key] = doc[self.key]

        if 'oauth_verifier' in request.args:
            try:
                data = self.remote.handle_oauth1_response()
            except OAuthException as e:
                data = e
        elif 'code' in request.args:
            try:
                data = self.remote.handle_oauth2_response()
            except OAuthException as e:
                data = e
        else:
            data

    def _tokengetter(self):
        return (self.doc["oauth_token"], self.doc["oauth_secret"])


class Facebook(OAuthProvider):
    name = "facebook"
    config = dict(base_url='https://graph.facebook.com/',
                  request_token_url=None,
                  access_token_url='/oauth/access_token',
                  authorize_url='https://www.facebook.com/dialog/oauth',
                  app_key='FACEBOOK',
                  request_token_params={'scope': 'email'})


class Twitter(OAuthProvider):
    name = "twitter"
    config = dict(base_url='https://api.twitter.com/1/',
                  request_token_url='https://api.twitter.com/oauth/request_token',
                  access_token_url='https://api.twitter.com/oauth/access_token',
                  authorize_url='https://api.twitter.com/oauth/authenticate',
                  app_key='TWITTER')

PROVIDERS = {
    "facebook": lambda app: Facebook(app),
    "twitter": lambda app: Twitter(app),
}
