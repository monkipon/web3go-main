import asyncio
import random
import art
import time

from web3go import Web3Go
from utils import read_private_keys, read_proxies


async def process_private_key(private_key, proxies, semaphore):
    async with semaphore:
        async with Web3Go(private_key, proxies) as web3go_bot:
            result = await web3go_bot.claim()
            streak = await web3go_bot.get_streak_days()
            leafs = await web3go_bot.get_info_about()
            # print(f"{web3go_bot.address} | {leafs} | {web3go_bot.proxy_ip}")
            print(f"{web3go_bot.address} | {result} | {streak} | {leafs} | {web3go_bot.proxy_ip}")


def make_art():
    art_text = art.text2art('Web3Go')
    lines = "-" * len(art_text.split('\n')[0])
    print(f"{lines}\n{art_text}{lines}")
    print('Создатель: https://t.me/Genjurx')


async def main():
    make_art()
    time1 = time.time()

    private_keys = await read_private_keys('keys.txt')
    proxies = await read_proxies('proxies.txt')

    semaphore = asyncio.Semaphore(10)

    tasks = [process_private_key(private_key, proxies[i % len(proxies)], semaphore) for i, private_key in
             enumerate(private_keys)]

    await asyncio.gather(*tasks)

    time2 = time.time()
    final_time = time2 - time1
    print(final_time)


if __name__ == "__main__":
    asyncio.run(main())
