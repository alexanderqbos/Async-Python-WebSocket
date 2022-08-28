#!/usr/bin/python3

import asyncio
import sys

async def client(message):
    reader, writer = await asyncio.open_connection('localhost', 12345)
    writer.write(message.encode('utf-8') + b'\n')
    data = await reader.readline()
    print(f"Received: {data.decode('utf-8')}")
    writer.close()
    await writer.wait_closed()

if(len(sys.argv) != 2):
    print(f'{sys.argv[0]} needs one argument to transmit')
    sys.exit(-1)

asyncio.run(client(sys.argv[1]))