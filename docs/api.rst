API Documentation
=================

Basics
------

The API-Service can be queried and managed using HTTP-Calls
to `api.it-se.me` and it will answer with JSON-Formatted output.

This is just the basic API documentation. To understand the underlying
conceptional idea, please see :ref:concepts and :ref:faq.

.. Danger::
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

The following erros shall be expected to be handled accordingly
by your application

.. list-table:: 
  :header-rows: 1

  * - HTTP code
    - Code name
    - Description
    - Recommended Behaviour
  * - 401
    - Code name
    - Description
    - Recommended Behaviour



Register
--------

URL:
   /v1/register/<provider>/<provider_id>/<target>

Supported Methods:
   GET



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

