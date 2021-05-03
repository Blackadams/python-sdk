import os
import asyncio
from elarian import Customer, Elarian, MessagingChannel, PaymentStatus, PaymentChannel, CustomerNumberProvider

client = Elarian(
        org_id=os.getenv('ORG_ID'),
        app_id=os.getenv('APP_ID'),
        api_key=os.getenv('API_KEY'),
)


async def handle_ussd(notif, customer, app_data, callback):
    print(notif)
    print(app_data)
    print(customer)
    callback(None, app_data)


async def start():
    client.set_on_connection_pending(lambda: print('Pending...'))
    client.set_on_connecting(lambda: print('Connecting...'))
    client.set_on_connection_error(lambda err: print(err))
    client.set_on_connection_closed(lambda: print("Connection closed!"))
    client.set_on_connected(lambda: print("Connected! Ready to process requests!"))
    client.set_on_ussd_session(handle_ussd)

    await client.connect()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(start())
    loop.run_forever()
