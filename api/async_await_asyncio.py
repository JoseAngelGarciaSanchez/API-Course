import asyncio
import time


def q():
    time.sleep(3)
    print("Why can't programmers tell jokes?")


def a():
    print("Timing!")


def main():
    q()
    a()


main()


async def async_q():
    await asyncio.sleep(3)
    print("Why can't programmers tell jokes?")


async def async_a():
    print("Timing!")


async def async_main():
    await asyncio.gather(async_q(), async_a())


# asyncio.run(async_main())
