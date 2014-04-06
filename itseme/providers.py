from flask_oauthlib.client import OAuthRemoteApp, OAuthException
from flask import session, url_for, request

from util import json_exception, json_error, _generate_code

from itseme import tasks


class Provider(object):

    def __init__(self, app):
        self.app = app

    def register(self, doc):
        pass 

    def verify(self, doc):
        pass

class SimpleVerifyMixin(object):

    MY_KEY = "SP_CODE"
    GEN_LENGTH = 4

    def register(self, doc):
        code = _generate_code(self.GEN_LENGTH)
        doc[self.CODE_KEY] = code
        return self._register(doc["provider_id"], doc, code)

    def verify(self, doc):
        code = request.args.get("code", None)
        if not code:
            return json_error(400, "missing_code",
                              "You need to provide the code parameter")

        if code == doc[self.CODE_KEY]:
            doc["status"] = "confirmed"
            doc.pop(self.CODE_KEY)
            return

        return json_error(400, "faulty_code",
                          "Sorry, code doesn't match.")


class EmailProvider(SimpleVerifyMixin, Provider):

    CODE_KEY = "email_code"
    GEN_LENGTH = 6

    def _register(self, confirm_id, doc, code):
        url = url_for('verify', hashkey=doc["_id"], code=code)
        tasks.send_confirm_email.delay(confirm_id, code, url)


class XmppProvider(SimpleVerifyMixin, Provider):

    CODE_KEY = "xmpp_code"
    GEN_LENGTH = 4

    def _register(self, confirm_id, doc, code):
        message = {"text": "Verification Code: {0}".format(code),
                   "verify": {"code": code, "hash": doc["_id"]}}

        tasks.send_xmpp_message.delay(confirm_id, message)


class SmsProvider(SimpleVerifyMixin, Provider):

    CODE_KEY = "phone_code"
    GEN_LENGTH = 4

    def _register(self, confirm_id, doc, code):
        message = "It-se, you {0}? Verify with: {1}".format(
                    doc["target"], code)

        tasks.send_sms_message.delay(confirm_id, message)


class OAuthProvider(Provider):

    name = ""
    always_callback = False
    config = {}

    def __init__(self, app):
        self.app = app
        self.remote = OAuthRemoteApp(self, self.name, **self.config)
        self.key = '%s_oauthtok' % self.name

    def register(self, doc):
        callback = None
        if request.args.get('next') or self.always_callback:
            callback = url_for('verify', hashkey=doc["_id"],
                               _external=True,
                               next=request.args.get('next') or "/v1/verified")

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
                if self.app.debug: raise
                return json_exception(e)
        elif 'code' in request.args:
            try:
                data = self.remote.handle_oauth2_response()
            except OAuthException as e:
                if self.app.debug: raise
                return json_exception(e)
        else:
            return json_error(400, "missing_code",
                    "You need to provide either oauth_verifier or code")

        print data

        def getter():
            return data

        self.remote.tokengetter(getter)

        try:
            if not self.confirm(doc, data):
                return json_error(400, "wrong_user",
                        "The user doesn't match. Sorry")
        except Exception, e:
            if self.app.debug: raise
            return json_exception(e, 500)

        doc["status"] = "confirmed"

    def confirm(self, doc, data):
        raise NotImplementedError()


class Facebook(OAuthProvider):
    name = "facebook"
    always_callback = True
    config = dict(base_url='https://graph.facebook.com/',
                  request_token_url=None,
                  access_token_url='/oauth/access_token',
                  authorize_url='https://www.facebook.com/dialog/oauth',
                  app_key='FACEBOOK',
                  request_token_params={'scope': 'email'})

    def confirm(self, doc, data):
        user_data = self.remote.get("me?fields=username")
        return user_data.data["username"] == doc["provider_id"]


class Twitter(OAuthProvider):
    name = "twitter"
    always_callback = True
    config = dict(base_url='https://api.twitter.com/1.1/',
                  request_token_url='https://api.twitter.com/oauth/request_token',
                  access_token_url='https://api.twitter.com/oauth/access_token',
                  authorize_url='https://api.twitter.com/oauth/authorize',
                  app_key='TWITTER')

    def confirm(self, doc, data):
        return data["screen_name"] == doc["provider_id"]


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
    "phone": SmsProvider
}
