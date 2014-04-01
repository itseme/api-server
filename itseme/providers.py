from flask_oauthlib.client import OAuthRemoteApp
from flask import session, url_for, request

from util import json_exception, json_error


class Provider(object):
    def register(self, doc):
        pass

    def approve(self, doc):
        pass


class OAuthProvider(Provider):

    name = ""
    config = {}

    def __init__(self, app):
        self.app = app
        self.remote = OAuthRemoteApp(self, self.name, **self.config)
        self.remote.tokengetter(self._tokengetter)
        self.key = '%s_oauthtok' % self.name

    def register(self, doc):
        callback = None
        if request.args.get('next'):
          callback = url_for('approve', hashkey=doc["_id"],
                             next=request.args.get('next'))

        resp = self.remote.authorize(callback=callback)

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
                return json_exception(e)
        elif 'code' in request.args:
            try:
                data = self.remote.handle_oauth2_response()
            except OAuthException as e:
                return json_exception(e)
        else:
          return json_error()
        self.confirm

    def _tokengetter(self):
        return (self.doc["oauth_token"], self.doc["oauth_secret"])


class FacebookProvider(OAuthProvider):
    name = "facebook"
    config = dict(base_url='https://graph.facebook.com/',
                  request_token_url=None,
                  access_token_url='/oauth/access_token',
                  authorize_url='https://www.facebook.com/dialog/oauth',
                  app_key='FACEBOOK',
                  request_token_params={'scope': 'email'})


class TwitterProvider(OAuthProvider):
    name = "twitter"
    config = dict(base_url='https://api.twitter.com/1/',
                  request_token_url='https://api.twitter.com/oauth/request_token',
                  access_token_url='https://api.twitter.com/oauth/access_token',
                  authorize_url='https://api.twitter.com/oauth/authenticate',
                  app_key='TWITTER')

PROVIDERS = {
    "facebook": lambda app: FacebookProvider(app),
    "twitter": lambda app: TwitterProvider(app),
}
