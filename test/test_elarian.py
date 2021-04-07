import pytest
import asyncio
import time
from elarian.elarian import Elarian
from elarian.models import MessagingChannel, PaymentChannel, CustomerNumberProvider
from test import loop, api_key, app_id, org_id, sms_short_code, mpesa_paybill, purse_id


@pytest.fixture(scope="session", autouse=True)
def client():
    """Create a connection to Elarian backend"""
    client = Elarian(app_id=app_id, api_key=api_key, org_id=org_id)
    yield client
    loop.run_until_complete(client.disconnect())


def test_connect(client):
    """Function to test the connection to Elarian backend"""
    assert client.is_connected()


def test_generate_auth_token(client):
    """Function to test the generate_auth_token function"""
    response = loop.run_until_complete(client.generate_auth_token())
    assert all(elem in response for elem in ("token", "lifetime"))


def test_add_customer_reminder_by_tag(client):
    """Function to test the add_customer_reminder_by_tag function"""
    tag = {"key": "some-key", "value": "some-value"}
    reminder = {"key": "some-rem", "remind_at": time.time() + 60, "payload": "some str"}
    response = loop.run_until_complete(
        client.add_customer_reminder_by_tag(tag, reminder)
    )
    assert all(elem in response for elem in ("status", "description", "work_id"))


def test_cancel_customer_reminder_by_tag(client):
    """Function to test the cancel_customer_reminder_by_tag function"""
    tag = {"key": "some-key", "value": "some-value"}
    response = loop.run_until_complete(
        client.cancel_customer_reminder_by_tag(tag, "some-rem")
    )
    assert all(elem in response for elem in ("status", "description", "work_id"))


def test_send_message_by_tag(client):
    """Function to test the send_message_by_tag function"""
    tag = {"key": "some-key", "value": "some-value"}
    sms_channel = {"number": sms_short_code, "channel": 'sms'}
    message = {"body": {"text": "Hello From Python"}}
    response = loop.run_until_complete(
        client.send_message_by_tag(tag, sms_channel, message)
    )
    assert all(elem in response for elem in ("status", "description", "work_id"))


def test_initiate_payment(client):
    """Function to test the initiate_payment function"""
    debit_from = {
        "customer": {
            "customer_number": {
                "number": "+254718769882",
                "provider": 'cellular',
            },
            "channel_number": {
                "number": mpesa_paybill,
                "channel": 'cellular',
            },
        }
    }
    credit_to = {"purse": {"purse_id": purse_id}}

    cash = {"currency_code": "KES", "amount": 10.55}

    response = loop.run_until_complete(
        client.initiate_payment(
            value=cash, debit_party=debit_from, credit_party=credit_to
        )
    )
    assert all(
        elem in response
        for elem in (
            "status",
            "description",
            "transaction_id",
            "debit_customer_id",
            "credit_customer_id",
        )
    )


def test_disconnect(client):
    """Function to test the disconnection function"""
    loop.run_until_complete(client.disconnect())
    assert not client.is_connected()
