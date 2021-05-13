import pytest
from src.elarian.simulator import Simulator
from tests import (
    loop,
    api_key,
    app_id,
    org_id,
    customer_number,
    adopted_customer,
)


@pytest.fixture(scope="session", autouse=True)
def client():
    """Create a connection to Simulator backend"""
    connection = Simulator(app_id=app_id, api_key=api_key, org_id=org_id)
    client = loop.run_until_complete(connection.connect())
    yield client
    loop.run_until_complete(connection.disconnect())


def test_receive_message(client):
    """Function to test the receive_message simulator function"""
    response = loop.run_until_complete(
        client.receive_message("254712345678", customer_number, "1234567", [{"ussd": '*123#'}])
    )
    assert all(elem in response for elem in ("message", "status", "description"))


def test_receive_payment(client):
    """Function to test the receive_payment simulator function"""
    response = loop.run_until_complete(
        client.receive_payment(
            "254712345678",
            adopted_customer,
            "test-transaction-id",
            {"amount": 100, "currency_code": "KES"},
            "pending_confirmation",
        )
    )
    assert all(elem in response for elem in ("message", "status", "description"))


def test_update_payment_status(client):
    """Function to test the update_payment_status simulator function"""
    response = loop.run_until_complete(
        client.update_payment_status("test-transaction-id", "failed")
    )
    assert all(elem in response for elem in ("message", "status", "description"))
