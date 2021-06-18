import asyncio


async def myAsyncFunction() -> int:
    await asyncio.sleep(2)
    return 2


async def main():
    r = await myAsyncFunction()
    print(r)


if __name__ == '__main__':
    asyncio.run(main())
