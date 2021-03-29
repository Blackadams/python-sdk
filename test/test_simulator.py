import pytest
from elarian.client import Elarian
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
