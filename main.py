import asyncio
import random
import art

from web3go import Web3Go
from utils import read_private_keys, read_proxies

async def main():

    art_text = art.text2art('Web3Go') 
    lines = "-" * len(art_text.split('\n')[0])
    print(f"{lines}\n{art_text}{lines}")
    print('Создатель: https://t.me/Genjurx')

    private_keys = await read_private_keys('keys.txt')
    proxies = await read_proxies('proxies.txt')

    for private_key in private_keys:
        proxy = random.choice(proxies) if proxies else None
        async with Web3Go(private_key, proxy) as web3go_bot:
            result = await web3go_bot.claim()
            proxy_ipport = web3go_bot.proxy.split('@')
            print(f"{web3go_bot.address} | {result} | {proxy_ipport[1]}")

if __name__ == "__main__":
    asyncio.run(main())