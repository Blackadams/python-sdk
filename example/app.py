import os
import asyncio
from elarian import Elarian

client = Elarian(
        org_id=os.getenv('ORG_ID'),
        app_id=os.getenv('APP_ID'),
        api_key=os.getenv('API_KEY'),
        options={
            'allow_notifications': False
        }
)


async def run():
    print("Ready to go!")
    await asyncio.sleep(1)
    resp = await client.generate_auth_token()
    print(resp)
    await client.disconnect()


async def start():

    client.set_on_connection_pending(lambda: print('Pending...'))
    client.set_on_connecting(lambda: print('Connecting...'))
    client.set_on_connection_error(lambda err: print(err))
    client.set_on_connection_closed(lambda: print("Connection closed!"))
    client.set_on_connected(run)

    await client.connect()
    await asyncio.sleep(120)


if __name__ == "__main__":
    asyncio.run(start())
