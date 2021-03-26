import os
import asyncio
from elarian import Customer, Elarian, MessagingChannel, PaymentStatus, PaymentChannel, CustomerNumberProvider

client = Elarian(
        org_id=os.getenv('ORG_ID'),
        app_id=os.getenv('APP_ID'),
        api_key=os.getenv('API_KEY'),
)


async def run():
    print("Ready to go!")
    await asyncio.sleep(1)
    phone_number = '+254718769882'
    channel = {
        "number": os.getenv('SMS_SENDER_ID'),
        "channel": MessagingChannel.SMS
    }
    session_id = 'some-session'
    message_parts = [
        {
            "text": 'Hello Python'
        },
        {
            "location": {
                "latitude": 10,
                "longitude": 2,
                "label": "Some label",
                "address": "Some address"
            }
        }
    ]

    customer = Customer(client=client, number=phone_number)
    resp = await customer.get_state()
    print(resp)
    await client.disconnect()


async def start():

    client.set_on_connection_pending(lambda: print('Pending...'))
    client.set_on_connecting(lambda: print('Connecting...'))
    client.set_on_connection_error(lambda err: print(err))
    client.set_on_connection_closed(lambda: print("Connection closed!"))
    client.set_on_connected(run)

    await client.connect()
    await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(start())
