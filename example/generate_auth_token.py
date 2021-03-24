import asyncio
from elarian import Elarian


async def run():
    client = Elarian(
        org_id='test-org-id',
        app_id='test-app-id',
        api_key='test-api-key')
    await client.connect()
    await asyncio.sleep(1)
    resp = await client.generate_auth_token()
    print(resp)
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(run())
