from celery import Celery
from flask_mail import Mail, Message

celery = Celery()
mail = Mail()

from xmpp_client import SendMsgBot


@celery.task()
def send_confirm_email(to, code, url):
    message = Message("It'se you? Then type {}".format(code))
    message.add_recipient(to)

    message.body = """Hello

We've just received note, that this email wants
to be registered with it-se.me . Please open this
URL to confirm this has been sent by you

  {0}

Or type the following code into your app:

  {1}

If that wasn't triggered by you, feel free to delete
this message and accept our apology for the bother.

 Thanks
   Mario

""".format(url, code)

    message.html = """<p>Hello</p>
    <p>We've just received note, that this email wants to be
    registered with it-se.me . Please open this URL to confirm
    this has been sent by you</p>
    <p><a href="{0}">{0}<p>
    <p>Or type the following code into your app:
        <br><strong>{1}</strong>
    </p>
    <p>If that wasn't triggered by you, feel free to delete
    this message and accept our apology for the bother.</p>
    <p>Thanks<br>Mario</p>
""".format(url, code)

    mail.send(message)


@celery.task()
def send_xmpp_message(to, message):
    # pooling would be great
    client = SendMsgBot(celery.conf.get("JID", ""),
                        celery.conf.get("JID_PASSWORD", ""),
                        to, message)
    if client.connect():
        client.process(block=True)