from django.test import TestCase
from django.core import mail

from core.settings import EMAIL_HOST_USER

from payments.email_utils import send_email


class TestPaymentsFunctions(TestCase):

    def test_send_email(self):
        DEFAULT_CLIENT_EMAIL = 'test@gmail.com'
        send_email('test.com', DEFAULT_CLIENT_EMAIL)
        first_message = mail.outbox[0]

        self.assertEqual(first_message.subject, 'Successful Payment')
        self.assertEqual(first_message.body, 'test.com')
        self.assertEqual(first_message.from_email, EMAIL_HOST_USER)
        self.assertEqual(first_message.to, [DEFAULT_CLIENT_EMAIL])
