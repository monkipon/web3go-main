import asyncio
import random
import art
import time

from web3go import Web3Go
from utils import read_private_keys, read_proxies


async def process_private_key(private_key, proxies, semaphore):
    async with semaphore:
        proxy = random.choice(proxies) if proxies else None
        async with Web3Go(private_key, proxy) as web3go_bot:
            result = await web3go_bot.claim()
            print(f"{web3go_bot.address} | {result} | {web3go_bot.proxy_ip}")


async def main():
    art_text = art.text2art('Web3Go')
    lines = "-" * len(art_text.split('\n')[0])
    print(f"{lines}\n{art_text}{lines}")
    print('Создатель: https://t.me/Genjurx')
    time1 = time.time()
    private_keys = await read_private_keys('keys.txt')
    proxies = await read_proxies('proxies.txt')

    semaphore = asyncio.Semaphore(5)

    tasks = [process_private_key(private_key, proxies, semaphore) for private_key in private_keys]
    await asyncio.gather(*tasks)

    time2 = time.time()
    final_time = time2 - time1
    print(final_time)

if __name__ == "__main__":
    asyncio.run(main())
