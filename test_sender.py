#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    test_sender
    ~~~~~~~~~~~

    Run tests for Sender.

    :copyright: (c) 2016 by Shipeng Feng.
    :license: BSD, see LICENSE for more details.
"""
import sys
import unittest

from sender import Mail, Message, Attachment
from sender import SenderError


class BaseTestCase(unittest.TestCase):
    """Baseclass for all the tests that sender uses.  We use this
    BaseTestCase for code style consistency.
    """

    def setup(self):
        pass

    def teardown(self):
        pass

    def setUp(self):
        self.setup()

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.teardown()

    def assert_equal(self, first, second):
        return self.assertEqual(first, second)

    def assert_true(self, expr, msg=None):
        self.assertTrue(expr, msg)

    def assert_false(self, expr, msg=None):
        self.assertFalse(expr, msg)

    def assert_raises(self, exception, callable=None, *args, **kwargs):
        self.assertRaises(exception, callable, *args, **kwargs)

    def assert_in(self, first, second):
        self.assertIn(first, second)

    def assert_not_in(self, first, second):
        self.assertNotIn(first, second)

    def assert_isinstance(self, obj, cls):
        self.assertIsInstance(obj, cls)

    if sys.version_info[:2] == (2, 6):
        def assertIn(self, x, y):
            assert x in y, "%r not found in %r" % (x, y)

        def assertNotIn(self, x, y):
            assert x not in y, "%r unexpectedly in %r" % (x, y)

        def assertIsInstance(self, x, y):
            assert isinstance(x, y), "not isinstance(%r, %r)" % (x, y)


class MailTestCase(BaseTestCase):

    def test_global_fromaddr(self):
        pass


class MessageTestCase(BaseTestCase):

    def test_subject(self):
        msg = Message('test')
        self.assert_equal(msg.subject, 'test')
        msg = Message('test', fromaddr='from@example.com', to='to@example.com')
        self.assert_in(msg.subject, str(msg))

    def test_to(self):
        msg = Message(fromaddr='from@example.com', to='to@example.com')
        self.assert_equal(msg.to, set(['to@example.com']))
        self.assert_in('to@example.com', str(msg))
        msg = Message(to=['to01@example.com', 'to02@example.com'])
        self.assert_equal(msg.to, set(['to01@example.com',
                                       'to02@example.com']))

    def test_fromaddr(self):
        msg = Message(fromaddr='from@example.com', to='to@example.com')
        self.assert_equal(msg.fromaddr, 'from@example.com')
        self.assert_in('from@example.com', str(msg))
        msg = Message()
        msg.fromaddr = ('From', 'from@example.com')
        self.assert_in('<from@example.com>', str(msg))

    def test_cc(self):
        msg = Message(fromaddr='from@example.com', to='to@example.com',
                      cc='cc@example.com')
        self.assert_in('cc@example.com', str(msg))

    def test_bcc(self):
        msg = Message(fromaddr='from@example.com', to='to@example.com',
                      bcc='bcc@example.com')
        self.assert_not_in('bcc@example.com', str(msg))

    def test_reply_to(self):
        msg = Message(fromaddr='from@example.com', to='to@example.com',
                      reply_to='reply-to@example.com')
        self.assert_equal(msg.reply_to, 'reply-to@example.com')
        self.assert_in('reply-to@example.com', str(msg))

    def test_process_address(self):
        msg = Message(fromaddr=('From\r\n', 'from\r\n@example.com'),
                      to='to\r@example.com', reply_to='reply-to\n@example.com')
        self.assert_in('<from@example.com>', str(msg))
        self.assert_in('to@example.com', str(msg))
        self.assert_in('reply-to@example.com', str(msg))

    def test_charset(self):
        msg = Message()
        self.assert_equal(msg.charset, 'utf-8')
        msg = Message(charset='ascii')
        self.assert_equal(msg.charset, 'ascii')

    def test_extra_headers(self):
        msg = Message(fromaddr='from@example.com', to='to@example.com',
                      extra_headers={'Extra-Header-Test': 'Test'})
        self.assert_in('Extra-Header-Test: Test', str(msg))

    def test_mail_and_rcpt_options(self):
        msg = Message()
        self.assert_equal(msg.mail_options, [])
        self.assert_equal(msg.rcpt_options, [])
        msg = Message(mail_options=['BODY=8BITMIME'])
        self.assert_equal(msg.mail_options, ['BODY=8BITMIME'])
        msg = Message(rcpt_options=['NOTIFY=OK'])
        self.assert_equal(msg.rcpt_options, ['NOTIFY=OK'])

    def test_to_addrs(self):
        msg = Message(to='to@example.com')
        self.assert_equal(msg.to_addrs, set(['to@example.com']))
        msg = Message(to='to@example.com', cc='cc@example.com',
                      bcc=['bcc01@example.com', 'bcc02@example.com'])
        expected_to_addrs = set(['to@example.com', 'cc@example.com',
                                 'bcc01@example.com', 'bcc02@example.com'])
        self.assert_equal(msg.to_addrs, expected_to_addrs)
        msg = Message(to='to@example.com', cc='to@example.com')
        self.assert_equal(msg.to_addrs, set(['to@example.com']))

    def test_validate(self):
        msg = Message(fromaddr='from@example.com')
        self.assert_raises(SenderError, msg.validate)
        msg = Message(to='to@example.com')
        self.assert_raises(SenderError, msg.validate)
        msg = Message(subject='subject\r', fromaddr='from@example.com',
                      to='to@example.com')
        self.assert_raises(SenderError, msg.validate)
        msg = Message(subject='subject\n', fromaddr='from@example.com',
                      to='to@example.com')
        self.assert_raises(SenderError, msg.validate)

    def test_attach(self):
        msg = Message()
        att = Attachment()
        atts = [Attachment() for i in range(3)]
        msg.attach(att)
        self.assert_equal(msg.attachments, [att])
        msg.attach(atts)
        self.assert_equal(msg.attachments, [att] + atts)

    def test_attach_attachment(self):
        msg = Message()
        msg.attach_attachment('test.txt', 'text/plain', 'this is test')
        self.assert_equal(msg.attachments[0].filename, 'test.txt')
        self.assert_equal(msg.attachments[0].content_type, 'text/plain')
        self.assert_equal(msg.attachments[0].data, 'this is test')

    def test_plain_text(self):
        plain_text = 'Hello!\nIt works.'
        msg = Message(fromaddr='from@example.com', to='to@example.com',
                      body=plain_text)
        self.assert_equal(msg.body, plain_text)
        self.assert_in('Content-Type: text/plain', str(msg))

    def test_plain_text_with_attachments(self):
        msg = Message(fromaddr='from@example.com', to='to@example.com',
                      subject='hello', body='hello world')
        msg.attach_attachment(content_type='text/plain', data=b'this is test')
        self.assert_in('Content-Type: multipart/mixed', str(msg))

    def test_html(self):
        html_text = '<b>Hello</b><br/>It works.'
        msg = Message(fromaddr='from@example.com', to='to@example.com',
                      html=html_text)
        self.assert_equal(msg.html, html_text)
        self.assert_in('Content-Type: multipart/alternative', str(msg))

    def test_message_id(self):
        msg = Message(fromaddr='from@example.com', to='to@example.com')
        self.assert_in('Message-ID: %s' % msg.message_id, str(msg))

    def test_attachment_ascii_filename(self):
        msg = Message(fromaddr='from@example.com', to='to@example.com')
        msg.attach_attachment('my test doc.txt', 'text/plain', b'this is test')
        self.assert_in('Content-Disposition: attachment; filename='
                       '"my test doc.txt"', str(msg))

    def test_attachment_unicode_filename(self):
        msg = Message(fromaddr='from@example.com', to='to@example.com')
        # Chinese filename :)
        msg.attach_attachment(u'我的测试文档.txt', 'text/plain',
                              'this is test')
        self.assert_in('UTF8\'\'%E6%88%91%E7%9A%84%E6%B5%8B%E8%AF'
                       '%95%E6%96%87%E6%A1%A3.txt', str(msg))


class AttachmentTestCase(BaseTestCase):

    def test_disposition(self):
        attach = Attachment()
        self.assert_equal(attach.disposition, 'attachment')

    def test_headers(self):
        attach = Attachment()
        self.assert_equal(attach.headers, {})


class SenderTestCase(BaseTestCase):
    pass


def suite():
    """A testsuite that has all the sender tests.
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MailTestCase))
    suite.addTest(unittest.makeSuite(MessageTestCase))
    suite.addTest(unittest.makeSuite(AttachmentTestCase))
    suite.addTest(unittest.makeSuite(SenderTestCase))
    return suite


if __name__ == "__main__":
    unittest.main(__name__, defaultTest='suite')
