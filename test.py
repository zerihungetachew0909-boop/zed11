import asyncio
from telegram import Bot

async def main():
    bot = Bot("")
    me = await bot.get_me()
    print(me)

asyncio.run(main())