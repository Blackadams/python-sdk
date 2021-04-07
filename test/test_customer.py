import pytest

from elarian.customer import Customer
from elarian.elarian import Elarian
from test import (
    loop,
    api_key,
    app_id,
    org_id,
    sms_short_code,
    mpesa_paybill,
    purse_id,
    sms_sender_id,
    customer_number,
    adopted_customer,
)


@pytest.fixture(scope="session", autouse=True)
def client():
    """Create a connection to Elarian backend"""
    connection = Elarian(app_id=app_id, api_key=api_key, org_id=org_id)
    client = loop.run_until_complete(connection.connect())
    yield client
    loop.run_until_complete(connection.disconnect())


def test_get_state(client):
    """Function to test the get_state function"""
    customer = Customer(client, number='254711891648')
    response = loop.run_until_complete(customer.get_state())
    assert all(
        elem in response
        for elem in (
            "customer_id",
            "identity_state",
            "messaging_state",
            "payment_state",
            "activity_state",
        )
    )


def test_adopt_state(client):
    """Function to test the adopt_state function"""
    customer = Customer(client, id='some-customer-id')
    response = loop.run_until_complete(customer.adopt_state(adopted_customer))
    assert all(elem in response for elem in ("customer_id", "status", "description"))


def test_send_message(client):
    """Function to test the send_message function"""
    customer = Customer(client, number='+254711892648')
    messaging_channel = {"number": sms_sender_id, "channel": "sms"}
    message = {"body": {"text": "Python sms messaging test"}}
    response = loop.run_until_complete(
        customer.send_message(messaging_channel, message)
    )
    assert all(
        elem in response
        for elem in ("customer_id", "status", "description", "message_id", "session_id")
    )


def test_reply_to_message(client):
    """Function to test the reply_to_message function"""
    customer = Customer(client, id='some-customer-id')
    message = {"body": {"text": "Python sms messaging reply test"}}
    response = loop.run_until_complete(
        customer.reply_to_message("some-message-id", message)
    )
    assert all(
        elem in response
        for elem in ("customer_id", "status", "description", "message_id", "session_id")
    )


def test_update_activity(client):
    """Function to test the update_activity function"""
    customer = Customer(client, number='+254711892648')
    activity_channel = {"number": "some-test-number", "channel": "WEB"}
    activity = {
        "session_id": "some-session-id",
        "key": "some-key",
        "properties": {"ok": 1, "val": False},
    }
    response = loop.run_until_complete(
        customer.update_activity(activity_channel, activity)
    )
    assert all(elem in response for elem in ("customer_id", "status", "description"))


def test_update_messaging_consent(client):
    """Function to test the update_messaging_consent function"""
    customer = Customer(client, number='+254711892648')
    messaging_channel = {"number": sms_sender_id, "channel": "SMS"}
    response = loop.run_until_complete(customer.update_messaging_consent(messaging_channel))
    assert all(elem in response for elem in ("customer_id", "status", "description"))


def test_update_app_data(client):
    """Function to test the update_app_data function"""
    customer = Customer(client, number='+254711892648')
    data = {"key": "test-key", "hollow": 1020, "payload": {"a": "Test"}, "string_value": str.encode("test"), "bytes_val": str.encode("test")}
    response = loop.run_until_complete(customer.update_app_data(data))
    assert all(elem in response for elem in ("customer_id", "status", "description"))


def test_lease_app_data(client):
    """Function to test the lease_app_data function"""
    customer = Customer(client, number='+254711892648')
    data = {"a": {"name": "update_after_lease"}}
    loop.run_until_complete(customer.update_app_data(data))
    response = loop.run_until_complete(customer.lease_app_data())
    assert response["a"]["name"] == "update_after_lease"


def test_delete_app_data(client):
    """Function to test the delete_app_data function"""
    customer = Customer(client, number='+254711892648')
    response = loop.run_until_complete(customer.delete_app_data())
    assert all(elem in response for elem in ("customer_id", "status", "description"))


def test_update_metadata(client):
    """Function to test the update_metadata function"""
    customer = Customer(client, number='+254711892648')
    data = {"key": "test-key", "hollow": 1020, "payload": {"a": "Test"}}
    response = loop.run_until_complete(customer.update_metadata(data))
    assert all(elem in response for elem in ("customer_id", "status", "description"))
    response = loop.run_until_complete(customer.get_state())
    assert all(
        elem in response["identity_state"]["metadata"]
        for elem in ("key", "hollow", "payload")
    )


def test_delete_metadata(client):
    """Function to test the delete_metadata function"""
    customer = Customer(client, number='+254711892648')
    response = loop.run_until_complete(customer.delete_metadata(["hollow"]))
    assert all(elem in response for elem in ("customer_id", "status", "description"))
    response = loop.run_until_complete(customer.get_state())
    assert "hollow" not in response["identity_state"].metadata


def test_update_secondary_ids(client):
    """Function to test the update_secondary_ids function"""
    customer = Customer(client, number='+254711892648')
    data = [
        {"key": "passport", "value": "808083", "expires_at": 300000000},
        {
            "key": "huduma",
            "value": "808082",
            "expires_at": 500000000,
        },
    ]
    response = loop.run_until_complete(customer.update_secondary_ids(data))
    assert all(elem in response for elem in ("customer_id", "status", "description"))
    response = loop.run_until_complete(customer.get_state())
    assert list(value for elem, value in response["identity_state"].secondary_ids if value in ("passport", "huduma"))


def test_delete_secondary_ids(client):
    """Function to test the delete_secondary_ids function"""
    customer = Customer(client, number='+254711892648')
    response = loop.run_until_complete(
        customer.delete_secondary_ids([{"key": "huduma", "value": "808082"}])
    )
    assert all(elem in response for elem in ("customer_id", "status", "description"))
    response = loop.run_until_complete(customer.get_state())
    assert not list(value for elem, value in response["identity_state"].secondary_ids if value in ("huduma", "808082"))


def test_update_tags(client):
    """Function to test the update_tags function"""
    customer = Customer(client, number='+254711892648')
    response = loop.run_until_complete(
        customer.update_tags([{"key": "coffid", "value": "test"}])
    )
    assert all(elem in response for elem in ("customer_id", "status", "description"))
    response = loop.run_until_complete(customer.get_state())
    assert list(value for elem, value in response["identity_state"].tags if value in ("coffid", "test"))


def test_delete_tags(client):
    """Function to test the delete_tags function"""
    customer = Customer(client, number='+254711892648')
    response = loop.run_until_complete(
        customer.delete_tags(["coffid"])
    )
    assert all(elem in response for elem in ("customer_id", "status", "description"))
    response = loop.run_until_complete(customer.get_state())
    assert not list(value for elem, value in response["identity_state"].tags if value in ("coffid"))


def test_add_reminder(client):
    """Function to test the add_reminder function"""
    customer = Customer(client, number='+254711892648')
    reminder = {"key": "some-key", "remind_at": 50000, "payload": '{"a": 1, "c": "de"}'}
    response = loop.run_until_complete(customer.add_reminder(reminder))
    assert all(elem in response for elem in ("customer_id", "status", "description"))


def test_cancel_reminder(client):
    """Function to test the cancel_reminder function"""
    customer = Customer(client, number='+254711892648')
    response = loop.run_until_complete(customer.cancel_reminder("some-key"))
    assert all(elem in response for elem in ("customer_id", "status", "description"))
