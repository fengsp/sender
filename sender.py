# -*- coding: utf-8 -*-
"""
    sender
    ~~~~~~

    Python SMTP Client for Humans.

    :copyright: (c) 2016 by Shipeng Feng.
    :license: BSD, see LICENSE for more details.
"""

__version__ = '0.3'

import sys
import smtplib
import time
from email import charset
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid, formataddr, parseaddr, formatdate
from email.header import Header


charset.add_charset('utf-8', charset.SHORTEST, None, 'utf-8')


PY2 = sys.version_info[0] == 2
if not PY2:
    text_type = str
    string_types = (str,)
    integer_types = (int,)

    iterkeys = lambda d: iter(d.keys())
    itervalues = lambda d: iter(d.values())
    iteritems = lambda d: iter(d.items())
else:
    text_type = unicode
    string_types = (str, unicode)
    integer_types = (int, long)

    iterkeys = lambda d: d.iterkeys()
    itervalues = lambda d: d.itervalues()
    iteritems = lambda d: d.iteritems()


class Mail(object):
    """Sender Mail main class.  This class is used for manage SMTP server
    connections and send messages.

    :param host: smtp server host, default to be 'localhost'
    :param username: smtp server authentication username
    :param password: smtp server authentication password
    :param port: smtp server port, default to be 25
    :param use_tls: put the SMTP connection in TLS (Transport Layer Security)
                    mode, default to be False
    :param use_ssl: put the SMTP connection in SSL mode, default to be False
    :param debug_level: the debug output level
    :param fromaddr: default sender for all messages sent by this mail instance
    """

    def __init__(self, host='localhost', username=None, password=None,
                 port=25, use_tls=False, use_ssl=False, debug_level=None,
                 fromaddr=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.use_ssl = use_ssl
        self.debug_level = debug_level
        self.fromaddr = fromaddr

    @property
    def connection(self):
        """Open one connection to the SMTP server.
        """
        return Connection(self)

    def send(self, message_or_messages):
        """Sends a single messsage or multiple messages.

        :param message_or_messages: one message instance or one iterable of
                                    message instances.
        """
        try:
            messages = iter(message_or_messages)
        except TypeError:
            messages = [message_or_messages]

        with self.connection as c:
            for message in messages:
                if self.fromaddr and not message.fromaddr:
                    message.fromaddr = self.fromaddr
                message.validate()
                c.send(message)

    def send_message(self, *args, **kwargs):
        """Shortcut for send.
        """
        self.send(Message(*args, **kwargs))


class Connection(object):
    """This class handles connection to the SMTP server.  Instance of this
    class would be one context manager so that you do not have to manage
    connection close manually.

    TODO: connection pool?

    :param mail: one mail instance
    """

    def __init__(self, mail):
        self.mail = mail

    def __enter__(self):
        if self.mail.use_ssl:
            server = smtplib.SMTP_SSL(self.mail.host, self.mail.port)
        else:
            server = smtplib.SMTP(self.mail.host, self.mail.port)

        # Set the debug output level
        if self.mail.debug_level is not None:
            server.set_debuglevel(int(self.mail.debug_level))

        if self.mail.use_tls:
            server.starttls()

        if self.mail.username and self.mail.password:
            server.login(self.mail.username, self.mail.password)

        self.server = server

        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.server.quit()

    def send(self, message):
        """Send one message instance.

        :param message: one message instance.
        """
        self.server.sendmail(message.fromaddr, message.to_addrs,
                             str(message) if PY2 else message.as_bytes(),
                             message.mail_options, message.rcpt_options)


class AddressAttribute(object):
    """Makes an address attribute forward to the addrs"""

    def __init__(self, name):
        self.__name__ = name

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return obj.addrs[self.__name__]

    def __set__(self, obj, value):
        if value is None:
            obj.addrs[self.__name__] = value
            return

        if self.__name__ in ('to', 'cc', 'bcc'):
            if isinstance(value, string_types):
                value = [value]
        if self.__name__ == 'fromaddr':
            value = process_address(parse_fromaddr(value), obj.charset)
        elif self.__name__ in ('to', 'cc', 'bcc'):
            value = set(process_addresses(value, obj.charset))
        elif self.__name__ == 'reply_to':
            value = process_address(value, obj.charset)
        obj.addrs[self.__name__] = value


class Message(object):
    """One email message.

    :param subject: message subject
    :param to: message recipient, should be one or a list of addresses
    :param body: plain text content body
    :param html: HTML content body
    :param fromaddr: message sender, can be one address or a two-element tuple
    :param cc: CC list, should be one or a list of addresses
    :param bcc: BCC list, should be one or a list of addresses
    :param attachments: a list of attachment instances
    :param reply_to: reply-to address
    :param date: message send date, seconds since the Epoch,
                 default to be time.time()
    :param charset: message charset, default to be 'utf-8'
    :param extra_headers: a dictionary of extra headers
    :param mail_options: a list of ESMTP options used in MAIL FROM commands
    :param rcpt_options: a list of ESMTP options used in RCPT commands
    """

    to = AddressAttribute('to')
    fromaddr = AddressAttribute('fromaddr')
    cc = AddressAttribute('cc')
    bcc = AddressAttribute('bcc')
    reply_to = AddressAttribute('reply_to')

    def __init__(self, subject=None, to=None, body=None, html=None,
                 fromaddr=None, cc=None, bcc=None, attachments=None,
                 reply_to=None, date=None, charset='utf-8',
                 extra_headers=None, mail_options=None, rcpt_options=None):
        self.message_id = make_msgid()
        self.subject = subject
        self.body = body
        self.html = html
        self.attachments = attachments or []
        self.date = date
        self.charset = charset
        self.extra_headers = extra_headers
        self.mail_options = mail_options or []
        self.rcpt_options = rcpt_options or []
        # used for actual addresses store
        self.addrs = dict()
        # set address
        self.to = to or []
        self.fromaddr = fromaddr
        self.cc = cc or []
        self.bcc = bcc or []
        self.reply_to = reply_to

    @property
    def to_addrs(self):
        return self.to | self.cc | self.bcc

    def validate(self):
        """Do email message validation.
        """
        if not (self.to or self.cc or self.bcc):
            raise SenderError("does not specify any recipients(to,cc,bcc)")
        if not self.fromaddr:
            raise SenderError("does not specify fromaddr(sender)")
        for c in '\r\n':
            if self.subject and (c in self.subject):
                raise SenderError('newline is not allowed in subject')

    def as_string(self):
        """The message string.
        """
        if self.date is None:
            self.date = time.time()

        if not self.html:
            if len(self.attachments) == 0:
                # plain text
                msg = MIMEText(self.body, 'plain', self.charset)
            elif len(self.attachments) > 0:
                # plain text with attachments
                msg = MIMEMultipart()
                msg.attach(MIMEText(self.body, 'plain', self.charset))
        else:
            msg = MIMEMultipart()
            alternative = MIMEMultipart('alternative')
            alternative.attach(MIMEText(self.body, 'plain', self.charset))
            alternative.attach(MIMEText(self.html, 'html', self.charset))
            msg.attach(alternative)

        msg['Subject'] = Header(self.subject, self.charset)
        msg['From'] = self.fromaddr
        msg['To'] = ', '.join(self.to)
        msg['Date'] = formatdate(self.date, localtime=True)
        msg['Message-ID'] = self.message_id
        if self.cc:
            msg['Cc'] = ', '.join(self.cc)
        if self.reply_to:
            msg['Reply-To'] = self.reply_to
        if self.extra_headers:
            for key, value in self.extra_headers.items():
                msg[key] = value

        for attachment in self.attachments:
            f = MIMEBase(*attachment.content_type.split('/'))
            f.set_payload(attachment.data)
            encode_base64(f)
            if attachment.filename is None:
                filename = str(None)
            else:
                filename = force_text(attachment.filename, self.charset)
            try:
                filename.encode('ascii')
            except UnicodeEncodeError:
                if PY2:
                    filename = filename.encode('utf-8')
                filename = ('UTF8', '', filename)
            f.add_header('Content-Disposition', attachment.disposition,
                         filename=filename)
            for key, value in attachment.headers.items():
                f.add_header(key, value)
            msg.attach(f)

        return msg.as_string()

    def as_bytes(self):
        return self.as_string().encode(self.charset or 'utf-8')

    def __str__(self):
        return self.as_string()

    def attach(self, attachment_or_attachments):
        """Adds one or a list of attachments to the message.

        :param attachment_or_attachments: one or an iterable of attachments
        """
        try:
            attachments = iter(attachment_or_attachments)
        except TypeError:
            attachments = [attachment_or_attachments]
        self.attachments.extend(attachments)

    def attach_attachment(self, *args, **kwargs):
        """Shortcut for attach.
        """
        self.attach(Attachment(*args, **kwargs))


class Attachment(object):
    """File attachment information.

    :param filename: filename
    :param content_type: file mimetype
    :param data: raw data
    :param disposition: content-disposition, default to be 'attachment'
    :param headers: a dictionary of headers, default to be {}
    """

    def __init__(self, filename=None, content_type=None, data=None,
                 disposition='attachment', headers={}):
        self.filename = filename
        self.content_type = content_type
        self.data = data
        self.disposition = disposition
        self.headers = headers


def parse_fromaddr(fromaddr):
    """Generate an RFC 822 from-address string.

    Simple usage::

        >>> parse_fromaddr('from@example.com')
        'from@example.com'
        >>> parse_fromaddr(('from', 'from@example.com'))
        'from <from@example.com>'

    :param fromaddr: string or tuple
    """
    if isinstance(fromaddr, tuple):
        fromaddr = "%s <%s>" % fromaddr
    return fromaddr


class SenderUnicodeDecodeError(UnicodeDecodeError):
    def __init__(self, obj, *args):
        self.obj = obj
        UnicodeDecodeError.__init__(self, *args)

    def __str__(self):
        original = UnicodeDecodeError.__str__(self)
        return '%s. You passed in %r (%s)' % (original, self.obj,
                                              type(self.obj))


class SenderError(Exception):
    pass


def force_text(s, encoding='utf-8', errors='strict'):
    """Returns a unicode object representing 's'.  Treats bytestrings using
    the 'encoding' codec.

    :param s: one string
    :param encoding: the input encoding
    :param errors: values that are accepted by Python’s unicode() function
                   for its error handling
    """
    if isinstance(s, text_type):
        return s

    try:
        if not isinstance(s, string_types):
            if not PY2:
                if isinstance(s, bytes):
                    s = text_type(s, encoding, errors)
                else:
                    s = text_type(s)
            elif hasattr(s, '__unicode__'):
                s = s.__unicode__()
            else:
                s = text_type(bytes(s), encoding, errors)
        else:
            s = s.decode(encoding, errors)
    except UnicodeDecodeError as e:
        if not isinstance(s, Exception):
            raise SenderUnicodeDecodeError(s, *e.args)
        else:
            s = ' '.join([force_text(arg, encoding, errors) for arg in s])
    return s


def process_address(address, encoding='utf-8'):
    """Process one email address.

    :param address: email from-address string
    """
    name, addr = parseaddr(force_text(address, encoding))

    try:
        name = Header(name, encoding).encode()
    except UnicodeEncodeError:
        name = Header(name, 'utf-8').encode()
    try:
        addr.encode('ascii')
    except UnicodeEncodeError:
        if '@' in addr:
            localpart, domain = addr.split('@', 1)
            localpart = str(Header(localpart, encoding))
            domain = domain.encode('idna').decode('ascii')
            addr = '@'.join([localpart, domain])
        else:
            addr = Header(addr, encoding).encode()
    return formataddr((name, addr))


def process_addresses(addresses, encoding='utf-8'):
    return map(lambda e: process_address(e, encoding), addresses)
