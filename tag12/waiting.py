import asyncio
from time import perf_counter

async def notice(name):
    print("Start:", name)
    await asyncio.sleep(0.4)
    print("Fertig:", name)
    return name


async def main():
    start = perf_counter()
    room = await notice("Raumhinweis")
    materials = await notice("Materialhinweis")
    print("Nacheinander:", perf_counter() - start, room, materials)

    start = perf_counter()
    room, materials = await asyncio.gather(notice("Raumhinweis"), notice("Materialhinweis"))

    print("Nebenläufig:", perf_counter() - start, room, materials)

if __name__ == "__main__":
    asyncio.run(main())
