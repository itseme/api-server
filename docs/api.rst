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
example:

.. code-block:: json

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
as follows:

.. code-block:: json

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

Optional Parameters:
   code=XXXX

In order to verify a previously registered entry of `hashkey`.
Commonly called with a `code` parameter containing the code
send through the providing channel. Also used as the callback
endpoint for some OAuth2-based providers like `Github` or `Facebook`.

If the given code matches the code in the system, a successful return
confirms the authentication happened and deleted the reference to
the previously provided `provider_id`. The returning JSON would like
like this:

.. code-block:: json

  {
   "confirmed": true
  }

But can also contain some further information given by the provider.

Errors
^^^^^^

404 - not_found:
  There has no pending entry been found for the hashkey. In case you
  have recently registered the account and reused the hashkey, this
  most commonly means the account has been verified meanwhile. You
  might want to use `confirm` to confirm this though.

400 - missing_code:
  The provider requires you to provide a `code` parameter but none
  has been given. Please prompt the User to enter the code and try
  again.

400 - faulty_code:
  The code provided doesn't match the one last send through the
  channel. Most commonly because another resend-registration-request
  has been triggered meanwhile and superseeded the used code. Please
  prompt the User that the code was wrong and that they might wait
  for another to arrive to retry or check for typing mistakes.

401 - OAuthException:
  A problem occured in the OAuth interna of the `twitter`, `facebook`
  or `github` providers. Please look at the provided `message` for
  further information. Most likely happens because of faulty
  redirection, failure in authentication with the service or missing
  parameters during development.

400 - wrong_user:
  In case of OAuth, the provided `provider_id` doesn't match with the
  one presented by the OAuth provider after authentication. Please
  prompt this to the User and explain them the requested account
  data didn't match their input. They might simply picked the wrong
  account when logging in.

500 - internal server error:
  Please provider a bug report something went terribly wrong on the
  server side.


Contact
-------

URL:
   /v1/contact/

Supported Methods:
   POST

Post data (JSON-formatted String):

.. code-block:: json

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

A post request asking the service to send a contact request to all
provided hashes in `contacts`. A core feature of the service: takes
all provided contact_info, makes them into hashes and matches them
against their database entry. Only those matching the given target
will be forwarded to the clients.

Secondly, looks up the targets of the specified clients and sends
every one found the `target` as well as the list of confirmed contact
infos for matching against their own address book. See
:ref:`contact-matching`. The send will be done via XMPP using the
itseme-extension in messages, see :ref:`itseme-contact-extension`.

If everything goes well and independant of the number of matches found
(even if none), the returning response will be:

.. code-block:: json

  {
    "status": "requests_send"
  }


Errors
^^^^^^

400 - json_decode_error:
  The provided JSON couldn't be read. Please make sure you've encoded
  it properly.

401 - target_unconfirmed:
  If the given `target` hasn't been successfully confirmed yet. You
  might want to resend the register-code for the jabber-id.

400 - key_error:
  You forgot to provide at least one of the mandatory keys. Please consult 'message' to learn which one.

400 - value_error:
  At least one of the provided parameters didn't match the required
  criteria. Please consult 'message' for further information.

400 - insufficient_contact_info:
  None of the provided contact info could be confirmed against the
  service, no requests will be send. At least one contact details
  needs to be provided and needs to be confirmed on the platform
  otherwise we won't forward the request. If you see this error,
  you might want to ask the user again to authenticate against
  at least one service.

413 - too_many_requested:
  Per request only not more than 100 hashes shall be provided. Please
  check before sending and batch the requests accordingly, preferably
  after the previous succeded to not run into the rate limit.

Confirm
-------

URL:
   /v1/confirm/<hashkey>/<target>

Supported Methods:
   GET

Confirm that the given `hashkey` links to the provided `target`.
Returns a json if and only if the hashkey was found and the stored
target matches the provided one:

.. code-block:: json


  {"confirmed": true}

In any other case (also if the key wasn't found or isn't verified yet)
it will return a false value for the check:

.. code-block:: json

  {"confirmed": false}

Errors
^^^^^^

There are no custom errors.

Confirm many
------------

URL:
   /v1/confirm

Supported Methods:
   POST

Post Data:

.. code-block:: json

  {
    "hashes": [
      "397ee3ee893ba686b8f228078803ce34911b35c8bf15a7986310de1225589fe13706a3242376da92c144a0e38e4693ac237840879947dc984870715c08793909",
      "e5d20f91694fde312aeb9e784178c8bd8a386d8c2789dfed7dc14a35fb8ea88fd0a1583a0a98b80058e8c9e6d7c8acd2f8c7ab240709600854f7e0bdabbc7078"
    ],
    "target": "jid@example.com"
   }


Confirm that the given `hashes` all link to the provided `target`.
Returns a json if so:

.. code-block:: json

  {"confirmed": true}

If at least one hashkey wasn't found, isn't confirmed yet or doesn't
match the provided target, it will return a falsy value instead:

.. code-block:: json

  {"confirmed": false}

Errors
^^^^^^

There are no custom errors.

Version
-------


URL:
   /version

Supported Methods:
   GET

Returns a json-response confirming the server version. Mainly for
debugging purposes:

.. code-block:: json

  {"version": "0.9-rc2"}
