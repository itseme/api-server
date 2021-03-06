#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2010  Nathanael C. Fritz
    This file is part of SleekXMPP.

    See the file LICENSE for copying permission.
"""

import sys
import logging
import getpass
from optparse import OptionParser
from sleekxmpp.xmlstream import ElementBase, register_stanza_plugin
from sleekxmpp import Message

from util import _generate_code, _make_key

import sleekxmpp

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input


class VerifyRequest(ElementBase):
    name = "verify"
    namespace = 'it-se.me:verify'
    plugin_attrib = "verify"
    interfaces = set(('code', 'hash'))
    sub_interfaces = interfaces


class ContactRequest(ElementBase):
    name = "contact"
    namespace = 'it-se.me:contact'
    plugin_attrib = "contact"
    interfaces = set(('jid', 'info'))
    sub_interfaces = interfaces


class SendMsgBot(sleekxmpp.ClientXMPP):

    """
    A basic SleekXMPP bot that will log in, send a message,
    and then log out.
    """

    def __init__(self, jid, password, recipients, message):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        # The message we wish to send, and the JID that
        # will receive it.
        if not isinstance(recipients, list):
            recipients = [recipients]
        self.recipients = recipients

        if isinstance(message, basestring):
            message = {"text": message}

        self.msg = message

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        register_stanza_plugin(Message, VerifyRequest)
        register_stanza_plugin(Message, ContactRequest)

        self.add_event_handler("session_start", self.start, threaded=True)

    def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.send_presence()
        self.get_roster()

        for recipient in self.recipients:
            text = self.msg["text"]
            message = self.make_message(recipient, text, None,
                                        "chat", None, None, None)

            if "verify" in self.msg:
                for key, value in self.msg["verify"].iteritems():
                    message["verify"][key] = value
            if "contact" in self.msg:
                for key, value in self.msg["contact"].iteritems():
                    message["contact"][key] = value

            message.send()

        # Using wait=True ensures that the send queue will be
        # emptied before ending the session.
        self.disconnect(wait=True)


if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    optp.add_option("-t", "--to", dest="to",
                    help="JID to send the message to")
    optp.add_option("-m", "--message", dest="message",
                    help="message to send")

    optp.add_option("--verify", dest="verify",
                    action='store_true', help="attach verify request")

    optp.add_option("--contact", dest="contact",
                    action='store_true', help="attach contact request")

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    if opts.jid is None:
        opts.jid = raw_input("Username: ")
    if opts.password is None:
        opts.password = getpass.getpass("Password: ")
    if opts.to is None:
        opts.to = raw_input("Send To: ")
    if opts.message is None:
        opts.message = raw_input("Message: ")

    message = {"text": opts.message}

    if opts.verify:
        message["verify"] = {"code": _generate_code(), "hash": _make_key(_generate_code(6), _generate_code(6))}

    if opts.contact:
        message["contact"] = {"jid": "random@example.com", "info": "info block as json"}

    # Setup the EchoBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = SendMsgBot(opts.jid, opts.password, opts.to, message)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0199') # XMPP Ping

    # If you are working with an OpenFire server, you may need
    # to adjust the SSL version used:
    # xmpp.ssl_version = ssl.PROTOCOL_SSLv3

    # If you want to verify the SSL certificates offered by a server:
    # xmpp.ca_certs = "path/to/ca/cert"

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        # If you do not have the dnspython library installed, you will need
        # to manually specify the name of the server if it does not match
        # the one in the JID. For example, to use Google Talk you would
        # need to use:
        #
        # 
        #     ...
        xmpp.process(block=True)
        print("Done")
    else:
        print("Unable to connect.")
