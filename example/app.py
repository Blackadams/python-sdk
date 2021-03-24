import os
import asyncio
from elarian import Elarian

client = Elarian(
        org_id=os.getenv('ORG_ID'),
        app_id=os.getenv('APP_ID'),
        api_key=os.getenv('API_KEY'))


async def run():
    print("Ready to go!")
    await asyncio.sleep(1)
    resp = await client.generate_auth_token()
    print(resp)
    await client.disconnect()


async def start():
    await client\
        .on('pending', lambda: print('Pending...'))\
        .on('connecting', lambda: print('Connecting...'))\
        .on('connected', run)\
        .on('closed', lambda: print("Connection closed!"))\
        .on('error', lambda err: print(err))\
        .connect()
    await asyncio.sleep(10000)


if __name__ == "__main__":
    asyncio.run(start())
