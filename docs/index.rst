Sender
======

.. module:: sender

Sender provides a simple interface to set up SMTP and send email messages.


Installation
------------

Install with the following command::
    
    $ pip install sender


Quickstart
----------

Sender is really easy to use.  Emails are managed through a :class:`Mail`
instance::
    
    from sender import Mail

    mail = Mail()

    mail.send_message("Hello", fromaddr="from@example.com",
                      to="to@example.com", body="Hello world!")


Message
-------

To send one message, we need to create a :class:`Message` instance::
    
    from sender import Message

    msg = Message("demo subject", fromaddr="from@example.com",
                  to="to@example.com")

You can also set attribute individually::
    
    msg.body = "demo body"

It is possible to set ``fromaddr`` with a two-element tuple::
    
    # fromaddr will be "Name <name@example.com>"
    msg = Message("Hello", fromaddr=("Name", "name@example.com"))

The message could have a plain text body and(or) HTML::
    
    msg.body = "hello"
    msg.html = "<h1>hello</h1>"

Let's construct one full message with all options::
    
    msg = Message("msg subject")
    msg.fromaddr = ("Admin", "admin@example.com")
    msg.to = "to@example.com"
    msg.body = "this is a msg plain text body"
    msg.html = "<b>Hello</b>"
    msg.cc = "cc@example.com"
    msg.bcc = ["bcc01@example.com", "bcc02@example.com"]
    msg.reply_to = "reply@example.com"
    msg.date = time.time()
    msg.charset = "utf-8"
    msg.extra_headers = {}
    msg.mail_options = []
    msg.rcpt_options = []


Mail
----

To connect to the SMTP server and send messages, we need to create a
:class:`Mail` instance::
    
    from sender import Mail

    mail = Mail("localhost", port=25, username="username", password="pass",
                use_tls=False, use_ssl=False, debug_level=None)

You can set ``fromaddr`` to a mail instance, if the message sent by this mail
instance does not set ``fromaddr``, this global ``fromaddr`` will be used::
    
    mail.fromaddr = ("Name", "name@example.com")

Now let's send our messages::
    
    mail.send(msg)
    # or an iterable of messages
    mail.send([msg1, msg2, msg3])

There is one shortcut for sending one message quickly::
    
    mail.send_message("hello", to="to@example.com", body="hello body")


Attachment
----------

It is quite easy to add attachments, we need :class:`Attachment` instance::
    
    from sender import Attachment

    with open("logo.jpg") as f:
        attachment = Attachment("logo.jpg", "image/jpeg", f.read())

    msg.attach(attachment)

If you have multiple attachments::

    msg.attach(attach01)
    msg.attach(attach02)
    msg.attach(attach03)
    # or an iterable of attachments
    msg.attach((attach01, attach02, attach03))

There is one shortcut for attaching one attachment quickly::
    
    msg.attach_attachment("logo.jpg", "image/jpeg", raw_data)


API
---

.. autoclass:: Mail
   :members:

.. autoclass:: Message
   :members: attach, attach_attachment

.. autoclass:: Attachment


Contribute
----------

Pull requests are welcomed, thank you for your suggestions!
