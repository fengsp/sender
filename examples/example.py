# -*- coding: utf-8 -*-
"""
    example
    ~~~~~~~

    Demo simple SMTP mail.

    :copyright: (c) 2014 by Shipeng Feng.
    :license: BSD, see LICENSE for more details.
"""

from sender import Mail, Message


mail = Mail()
msg = Message("Hello", fromaddr="from@sender.com", to="to@sender.com",
              body="hello world from sender")
mail.send(msg)
