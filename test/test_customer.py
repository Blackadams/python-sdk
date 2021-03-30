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
    # client = Elarian(app_id=app_id, api_key=api_key, org_id=org_id)
    # yield client.connect()
    # loop.run_until_complete(client.disconnect())
    connection = Elarian(app_id=app_id, api_key=api_key, org_id=org_id)
    client = loop.run_until_complete(connection.connect())
    yield client
    loop.run_until_complete(connection.disconnect())
    # return Elarian(app_id=app_id, api_key=api_key, org_id=org_id)


# def test_connect(client):
#     loop.run_until_complete(client.connect())
#     assert client.is_connected()


def test_get_state(client):
    customer = Customer(client, 'some-customer-id')
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
    customer = Customer(client)
    response = customer.adopt_state(adopted_customer)
    assert all(elem in response for elem in ("customer_id", "status", "description"))


def test_send_message(client):
    customer = Customer(client)
    messaging_channel = {"number": sms_sender_id, "channel": "sms"}
    message = {"body": {"text:": "Python sms messaging test"}}
    response = loop.run_until_complete(
        customer.send_message(messaging_channel, message)
    )
    assert all(
        elem in response
        for elem in ("customer_id", "status", "description", "message_id", "session_id")
    )


def test_reply_to_message(client):
    customer = Customer(client)
    message = {"body": {"text": "Python sms messaging reply test"}}
    response = loop.run_until_complete(
        customer.reply_to_message("some-message-id", message)
    )
    assert all(
        elem in response
        for elem in ("customer_id", "status", "description", "message_id", "session_id")
    )


def test_update_activity(client):
    customer = Customer(client)
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
    customer = Customer(client)
    messaging_channel = {"number": sms_sender_id, "channel": "SMS"}
    response = loop.run_until_complete(customer.update_activity(messaging_channel))
    assert all(elem in response for elem in ("customer_id", "status", "description"))


def test_update_app_data(client):
    customer = Customer(client)
    data = {"key": "test-key", "hollow": 1020, "payload": {"a": "Test"}}
    response = loop.run_until_complete(customer.update_app_data(data))
    assert all(elem in response for elem in ("customer_id", "status", "description"))


def test_lease_app_data(client):
    customer = Customer(client)
    data = {"a": {"name": "update_after_lease"}}
    loop.run_until_complete(customer.update_app_data(data))
    response = loop.run_until_complete(customer.lease_app_data())
    assert response["abc"]["name"] == "update_after_lease"


def test_delete_app_data(client):
    customer = Customer(client)
    response = loop.run_until_complete(customer.delete_app_data())
    assert all(elem in response for elem in ("customer_id", "status", "description"))


def test_update_metadata(client):
    customer = Customer(client)
    data = {"key": "test-key", "hollow": 1020, "payload": {"a": "Test"}}
    response = loop.run_until_complete(customer.update_metadata(data))
    assert all(elem in response for elem in ("customer_id", "status", "description"))
    response = loop.run_until_complete(customer.get_state())
    assert all(
        elem in response["identity_state"]["metadata"]
        for elem in ("key", "hollow", "payload")
    )


def test_delete_metadata(client):
    customer = Customer(client)
    response = loop.run_until_complete(customer.delete_metadata(["hollow"]))
    assert all(elem in response for elem in ("customer_id", "status", "description"))
    response = loop.run_until_complete(customer.get_state())
    assert "hollow" not in response["identity_state"]["metadata"]


def test_update_secondary_ids(client):
    customer = Customer(client)
    data = [
        {"key": "passport", "value": "808083", "expiresAt": 300000000},
        {
            "key": "huduma",
            "value": "808082",
            "expiresAt": 500000000,
        },
    ]
    response = loop.run_until_complete(customer.update_app_data(data))
    assert all(elem in response for elem in ("customer_id", "status", "description"))


def test_delete_secondary_ids(client):
    customer = Customer(client)
    response = loop.run_until_complete(
        customer.delete_secondary_ids([{"key": "huduma", "value": "808082"}])
    )
    assert all(elem in response for elem in ("customer_id", "status", "description"))
    response = loop.run_until_complete(customer.get_state())
    # come back to this
    assert next(
        (
            value
            for value in response["identity_state"]["metadata"]
            if value["key"] == "huduma"
        ),
        False,
    )


def test_update_tags(client):
    customer = Customer(client)
    response = loop.run_until_complete(
        customer.delete_secondary_ids([{"key": "huduma", "value": "808082"}])
    )
    assert all(elem in response for elem in ("customer_id", "status", "description"))
    response = loop.run_until_complete(customer.get_state())
    # come back to this
    assert next(
        (
            value
            for value in response["identity_state"]["metadata"]
            if value["key"] == "huduma"
        ),
        False,
    )


def test_delete_tags(client):
    customer = Customer(client)
    response = loop.run_until_complete(
        customer.delete_secondary_ids([{"key": "huduma", "value": "808082"}])
    )
    assert all(elem in response for elem in ("customer_id", "status", "description"))
    response = loop.run_until_complete(customer.get_state())
    # come back to this
    assert next(
        (
            value
            for value in response["identity_state"]["metadata"]
            if value["key"] == "huduma"
        ),
        False,
    )


def test_add_reminder(client):
    customer = Customer(client)
    reminder = {"key": "some-key", "remindAt": 50000, "payload": {"a": 1, "c": "de"}}
    response = loop.run_until_complete(customer.add_reminder(reminder))
    assert all(elem in response for elem in ("customer_id", "status", "description"))


def test_cancel_reminder(client):
    customer = Customer(client)
    response = loop.run_until_complete(customer.cancel_reminder("some-key"))
    assert all(elem in response for elem in ("customer_id", "status", "description"))
