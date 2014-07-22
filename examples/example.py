# -*- coding: utf-8 -*-
"""
    example
    ~~~~~~~

    Demo simple SMTP mail.

    :copyright: (c) 2014 by Shipeng Feng.
    :license: BSD, see LICENSE for more details.
"""
from sender import Mail, Message, Attachment


SMTP_HOST = 'smtp.example.com'
SMTP_USER = 'user@example.com'
SMTP_PASS = 'password'
SMTP_ADDRESS = 'user@example.com'


mail = Mail(host=SMTP_HOST, username=SMTP_USER, password=SMTP_PASS,
            fromaddr=SMTP_ADDRESS)


msg01 = Message("Hello01", to="to@example.com", body="hello world")


msg02 = Message("Hello02", to="to@example.com")
msg02.fromaddr = ('no-reply', 'no-reply@example.com')
msg02.body = "hello world!"


msg03 = Message("Hello03", to="to@example.com")
msg03.fromaddr = (u'请勿回复', 'noreply@example.com')
msg03.body = u"你好世界" # Chinese :)
msg03.html = u"<b>你好世界</b>"


msg04 = Message("Hello04", body="Hello world 04")
msg04.to = "to@example.com"
msg04.cc = ["cc01@example.com", "cc02@example"]
msg04.bcc = ["bcc@example.com"]


msg05 = Message("Hello05", to="to@example.com", body="Hello world 05")
with open("../docs/_static/sender.png") as f:
    msg05.attach_attachment("sender.png", "image/png", f.read())


msg06 = Message("Hello06", to="to@example.com", body="Hello world 06")
with open("test.txt") as f:
    attachment = Attachment("test.txt", "text/plain", f.read())
msg06.attach(attachment)


mail.send([msg01, msg02, msg03, msg04, msg05, msg06])
