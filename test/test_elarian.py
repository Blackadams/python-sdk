
import unittest
import asyncio
import time
from elarian import Elarian, MessagingChannel, PaymentChannel, CustomerNumberProvider

from test import loop, api_key, app_id, org_id, sms_short_code, mpesa_paybill, purse_id

client = Elarian(app_id=app_id, api_key=api_key, org_id=org_id)

unittest.TestLoader.sortTestMethodsUsing = None


class Elarian(unittest.TestCase):

    def test_1_connect(self):
        loop.run_until_complete(client.connect())
        loop.run_until_complete(asyncio.sleep(2))
        self.assertTrue(client.is_connected())

    def test_2_generate_auth_token(self):
        res = loop.run_until_complete(client.generate_auth_token())
        self.assertIn('token', res)
        self.assertIn('lifetime', res)

    def test_3_add_customer_reminder_by_tag(self):
        tag = {
            'key': 'some-key',
            'value': 'some-value'
        }
        reminder = {
            'key': 'some-rem',
            'remind_at': time.time() + 60,
            'payload': 'some str'
        }
        res = loop.run_until_complete(client.add_customer_reminder_by_tag(tag=tag, reminder=reminder))
        self.assertIn('status', res)
        self.assertIn('description', res)
        self.assertIn('work_id', res)

    def test_4_cancel_customer_reminder_by_tag(self):
        tag = {
            'key': 'some-key',
            'value': 'some-value'
        }
        res = loop.run_until_complete(client.cancel_customer_reminder_by_tag(tag, reminder_key='some-rem'))
        self.assertIn('status', res)
        self.assertIn('description', res)
        self.assertIn('work_id', res)

    def test_5_send_message_by_tag(self):
        tag = {
            'key': 'some-key',
            'value': 'some-value'
        }
        sms_channel = {
            'number': sms_short_code,
            'channel': MessagingChannel.SMS
        }
        message = {
            'body': {
                'text': 'Hello From Python'
            }
        }
        res = loop.run_until_complete(
            client.send_message_by_tag(tag=tag, messaging_channel=sms_channel, message=message))
        self.assertIn('status', res)
        self.assertIn('description', res)
        self.assertIn('work_id', res)

    def test_6_initiate_payment(self):
        debit_from = {
            "customer": {
                "customer_number": {
                    "number": "+254718769882",
                    "provider": CustomerNumberProvider.CELLULAR
                },
                "channel_number": {
                    "number": mpesa_paybill,
                    "channel": PaymentChannel.CELLULAR
                }
            }
        }
        credit_to = {
            "purse": {
                "purse_id": purse_id
            }
        }

        cash = {'currency_code': 'KES', 'amount': 10.55}

        res = loop.run_until_complete(
            client.initiate_payment(value=cash, debit_party=debit_from, credit_party=credit_to))

        self.assertIn('status', res)
        self.assertIn('description', res)
        self.assertIn('transaction_id', res)
        self.assertIn('debit_customer_id', res)
        self.assertIn('credit_customer_id', res)

    def test_7_disconnect(self):
        loop.run_until_complete(client.disconnect())
        self.assertFalse(client.is_connected())


if __name__ == '__main__':
    unittest.main()
