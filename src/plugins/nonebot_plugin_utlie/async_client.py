import httpx

async def async_client(proxies={}, headers={}):

    async with httpx.AsyncClient(proxies=proxies, headers=headers) as client:
        yield client

    yield