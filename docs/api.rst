API Documentation
=================

Basics
------

The API-Service can be queried and managed using HTTP-Calls
to `api.it-se.me` and it will answer with JSON-Formatted output.

This is just the basic API documentation. To understand the underlying
conceptional idea, please see :ref:concepts and :ref:faq.

.. Warning::
   Though we consider the v1-API kind of stable and want to only
   add new features, it is still in a Beta-Testing phase and might
   be subject to change if problematic security concerns are raised.
   Please keep this a default-off extended feature in your
   (production) App until further notice.


Limitations
^^^^^^^^^^^

In order to allow wide, anonymous access to the API and foster
a wide addoption there is no App authentication necessary to use
the service. However, there is a rate limitatin of 10 request
we allow per second per IP. There might also be specific limitations
per call.


Error Codes and Messages
^^^^^^^^^^^^^^^^^^^^^^^^

For general Error reporting, we are using HTTP-Error-Codes. Further
those provide some insight of what went wrong as json like in this
example::

  {
      "error": {
        "code": "target_unconfirmed",
        "message": "Please confirm 'X' first."
       }
  }



Register
--------

URL:
   /v1/register/<provider>/<provider_id>/<target>

Supported Methods:
   GET

Optional Parameters:
  resend=1

With this method you can register a new entry to the service. You have
to specify the provider (medium) and the id on that one as well as the
target xmpp-id it should be bound to.

If you call it more often for the same `target` it will only send the
confirmation code once. If, and only if, the User asks for it to resend
please attach the "?resend=1" parameter to the call, which will
generate and send a new code.

If everything goes according to plan, you'll receive a json response
as follows::

 {
  "status": "pending",
  "hash": "397ee3ee893ba686b8f228078803ce34911b35c8bf15a7986310de1225589fe13706a3242376da92c144a0e38e4693ac237840879947dc984870715c08793909"
 }

The response might contain a `goto`-field containing a URL. If
present the APP *must* redirect the user to this URL to continue
authentication. Otherwise the confirmation code will be handled
in a different way (see providers).

.. NOTE::
   Before you can bound any medium to a jabber-id, you first need
   to confirm said ID by requesting the `provider` 'xmpp' with the
   given jabber-id as `provider_id` and `target`. For
   `xmpp@example.com` this would for example be
   `/v1/register/xmpp/xmpp@example.com/xmpp@example.com` and you
   won't be able to bind anything to this target until it has been
   verified.

Providers
^^^^^^^^^

Currently the following providers are support and acts as follows:

xmpp:
  The xmpp provider expects a jabber id as the `provider_id`. It
  will then connect to that account and send a four digit number
  to be used to verify against the server. This provider shall
  also be used to initially register a jabber id by providing the
  same id for `provider_id` and `target`. The app should either
  wait for that request or prompt the user to wait for that code.

email:
  Expects an email-address as `provider_id` and will then send a
  six digit verification code plus URL to the given Email-Address
  for confirmation. The App should inform the user about this and
  ask them to confirm manually.

phone:
  Expects the `provider_id` to be an international phone number
  including `+XXX` number codes. An example call would be:
  `/v1/register/phone/+1234456789/xmpp@example.com` . This provider
  will send a SMS with a four digit code to the given number.

facebook:
  The facebook provider expects your username as the `provider_id`.
  As it uses OAuth, the return will contain a `goto`-url the
  App should redirect the User to in order to sign in and grant
  the permissions

twitter:
  Similar to facebook the `provider_id` is expected to be the twitter
  username and it will also return a `goto`-url to redirect the User,
  too.

github:
  Same as for twitter and facebook, the expected `provider_id` is
  the username and there will be a `goto`-url returned to opened by
  the App for the User to authenticate against.


Errors
^^^^^^

401 - target_unconfirmed:
  If the given `target` hasn't been successfully confirmed yet. You
  might want to resend the register-code for your jabber-id


Verify
------
URL:
   /v1/verify/<hashkey>

Supported Methods:
   GET





Contact
-------

URL:
   /v1/contact/

Supported Methods:
   POST

Post data::

  {
    "target": "xmpp@example.com",
    "contact_info": [
        {"protocol": "phone", "id": "+00112345678"},
        {"protocol": "email", "id": "hunter@jobs.com"},
        {"protocol": "phone", "id": "+4912345"}
        ],
    "contacts": [
        "397ee3ee893ba686b8f228078803ce34911b35c8bf15a7986310de1225589fe13706a3242376da92c144a0e38e4693ac237840879947dc984870715c08793909",
        "e5d20f91694fde312aeb9e784178c8bd8a386d8c2789dfed7dc14a35fb8ea88fd0a1583a0a98b80058e8c9e6d7c8acd2f8c7ab240709600854f7e0bdabbc7078",
        "abce880ed2d448abffa8efa8939d8e15625ad16ff2330d97388f32fee480d799b9753e1d2f362c7deb1f7ea83bfbbf234712f9b45979496589812d0016e2cb48"
        ]
    }

Confirm
-------

URL:
   /v1/confirm/<string:hashkey>/<string:target>

Supported Methods:
   GET


Confirm many
------------

URL:
   /v1/confirm/<string:hashkey>

Supported Methods:
   POST

Post Data::

  {
    "hashes": [
      "397ee3ee893ba686b8f228078803ce34911b35c8bf15a7986310de1225589fe13706a3242376da92c144a0e38e4693ac237840879947dc984870715c08793909",
      "e5d20f91694fde312aeb9e784178c8bd8a386d8c2789dfed7dc14a35fb8ea88fd0a1583a0a98b80058e8c9e6d7c8acd2f8c7ab240709600854f7e0bdabbc7078"
    ],
    "target": "jid@example.com"
  }

