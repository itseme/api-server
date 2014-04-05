XMPP Extensions
===============

In order to allow an automatic, user-less flow for verification and
confirmation of apps, the It-se.me XMPP client sends slightly modified
versions of messages, containing extra information for seamless
integration. The extensions are done to the normal message-stanza and
are wrapped into the `it-se.me`-namespace and are of either `verify`
or `contact`


Sending codes
-------------

When the it-se.me service sends the verification code to the provided
jabber id, it does this through the message (for display) but also
attaches the verify-tag (in the `it-se.me`-namespace). This tag contains
to tags: `code` and `hash`. The `hash` contains the generated SHA512-Sum
while `code` contains the provided code:

.. code-block:: xml

   <message from='itseme@jabber.ccc.de/XXXXX' to='xmmp@example.com' type='chat' xml:lang='en'>
    <body>It-se, you xmmp@example.com? Verify with: 3991</body>
    <verify xmlns='it-se.me:verify'>
        <code>3991</code>
        <hash>fb1a59cd5e804c48d89f4267956518ac47b7d0e645fd92fcee85cbd9dbebb3eef4ad12a2d5baaa216ade5c698XXXXXXX8c0a5208f22b8aa9989dec91401</hash>
    </verify>
   </message>

When the app receives such a message and has a registration with
the given hash pending, it may automatically call the verify-url
providing the under `code`-lying content as a parameter to automatically
authenticate the service. In which case it is also recommended, to
prevent the message from being shown to the user.

.. Note::
   Though you there is a jabber account provided here, this might be
   subject to change and the implementation should not rely on it coming
   from this account.


.. :ref:`itseme-contact-extension`

Contacts Request
----------------

When an authenticated user sends a `contact`-request to the API and the
service finds matching hashes, it then forwards the _confirmed_ contact
details alongside the provided jabber-id to the jabber account stored
for that hash via an xmpp message, too. Those messages contain a
`contact`-tag of the `it-se.me`-namespace, similar to this:

.. code-block:: xml

   <message from='itseme@jabber.ccc.de/XXXXX' to='xmmp@example.com' type='chat' xml:lang='en'>
      <body>Hey there,
        xmpp2@example.com asked whether they are allowed to get in
        contact with you. They provided the following contact
        details for you to confirm their identity:
          * phone: +123456789
          * email: xmpp2@example.com
      </body>
      <contact xmlns='it-se.me:contact'>
            <info>[{"provider": "phone", "id": "+123456789",
            "confirmed": true}, {"provider": "email", "id":
            "xmpp2@example.com", "confirmed": true}]</info>
            <jid>random@example.com</jid>
      </contact>
    </message>

In which the `info`-tag contains an encoded JSON-Array with a list of
hashes in the form of:

.. code-block:: json

  {
    "provider": "email",
    "id": "xmpp2@example.com",
    "confirmed": true
  }

And the provided-`jid`-tag contains the corresponding target account
requesting the contact. As discussed in :ref:concept, the App may
use these provided information to look up the account in the Users
address book and (if it chooses to) add the account to their roster.
It is generally recommended to also subscribe to their presence and
immediatly send them a similar request containing the `contact`-tag
with your own verified contact details because up to this point the
other party has no information about ones account information.

.. Note::
   If the App receives a `contact` request from any other account
   than the specified one, it should always check back the provided
   contact information with the it-se.me service using the confirm-many
   API call. As this fails if at least one isn't confirmed the App
   may not send any contact information on its own that hasn't been
   verfified before hand.
