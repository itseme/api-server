from flask_oauthlib.client import OAuthRemoteApp, OAuthException
from flask import session, url_for, request

from util import json_exception, json_error

from itseme import tasks
import random


class Provider(object):

    def __init__(self, app):
        self.app = app

    def register(self, doc):
        pass

    def verify(self, doc):
        pass


class EmailProvider(Provider):

    def register(self, doc):
        target_id = doc["provider_id"]
        code = "{0:.6}".format(random.random())[2:]
        doc["email_code"] = code
        url = url_for('verify', hashkey=doc["_id"], code=code)
        tasks.send_confirm_email.delay(target_id, code, url)

    def verify(self, doc):
        code = request.args.get("code", None)
        if not code:
            return json_error(400, "missing_code", "You need to provide the code parameter")

        if code == doc["email_code"]:
            doc["status"] = "confirmed"
            doc.pop("email_code")
            return

        return json_error(400, "faulty_code", "Sorry, code doesn't match.")


class XmppProvider(Provider):

    def register(self, doc):
        target_id = doc["provider_id"]
        code = "{0:.4}".format(random.random())[2:]
        doc["xmpp_code"] = code
        message = "Verification Code: {0}".format(code)
        tasks.send_xmpp_message.delay(target_id, message)

    def verify(self, doc):
        code = request.args.get("code", None)
        if not code:
            return json_error(400, "missing_code", "You need to provide the code parameter")

        if code == doc["xmpp_code"]:
            doc["status"] = "confirmed"
            doc.pop("xmpp_code")
            return

        return json_error(400, "faulty_code", "Sorry, code doesn't match.")


class OAuthProvider(Provider):

    name = ""
    config = {}

    def __init__(self, app):
        self.app = app
        self.remote = OAuthRemoteApp(self, self.name, **self.config)
        self.key = '%s_oauthtok' % self.name

    def register(self, doc):
        callback = None
        if request.args.get('next'):
            callback = url_for('verify', hashkey=doc["_id"],
                               next=request.args.get('next'))

        resp = self.remote.authorize(callback=callback)

        if self.key in session:
            doc[self.key] = session.pop(self.key)

        return {"goto": resp.headers['Location']}

    def verify(self, doc):
        if self.key in doc:
            session[self.key] = doc.pop(self.key)

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
            return json_error(400, "missing_code", "You need to provide either oauth_verifier or code")

        try:
            if not self.confirm(doc, data):
                return json_error(400, "wrong_user", "The user doesn't match. Sorry")
        except Exception, e:
            return json_exception(500, e)

        doc["status"] = "confirmed"

    def confirm(self, doc, data):
        raise NotImplementedError()

class Facebook(OAuthProvider):
    name = "facebook"
    config = dict(base_url='https://graph.facebook.com/',
                  request_token_url=None,
                  access_token_url='/oauth/access_token',
                  authorize_url='https://www.facebook.com/dialog/oauth',
                  app_key='FACEBOOK',
                  request_token_params={'scope': 'email'})

    def confirm(self, doc, data):
        user_data = self.remote.get("me?fields=username")
        return user_data["username"] == doc["provider_id"]

class Twitter(OAuthProvider):
    name = "twitter"
    config = dict(base_url='https://api.twitter.com/1/',
                  request_token_url='https://api.twitter.com/oauth/request_token',
                  access_token_url='https://api.twitter.com/oauth/access_token',
                  authorize_url='https://api.twitter.com/oauth/authenticate',
                  app_key='TWITTER')

    def confirm(self, doc, data):
        user_data = self.remote.get("account/verify_credentials.json?skip_status=1")
        return user_data["screen_name"] == doc["provider_id"]


class Github(OAuthProvider):
    name = "github"
    config = dict(app_key="GITHUB",
                  request_token_params={'scope': 'user'},
                  base_url='https://api.github.com/',
                  request_token_url=None,
                  access_token_method='POST',
                  access_token_url='https://github.com/login/oauth/access_token',
                  authorize_url='https://github.com/login/oauth/authorize')

    def confirm(self, doc, data):
        user_data = self.remote.get("user")
        return user_data["login"] == doc["provider_id"]


PROVIDERS = {
    "facebook": Facebook,
    "twitter": Twitter,
    "github": Github,
    "email": EmailProvider,
    "xmpp": XmppProvider,
}
