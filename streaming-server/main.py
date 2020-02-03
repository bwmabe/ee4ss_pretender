#!/usr/bin/env python3

import asyncio

from datetime import datetime

# Global to handle pause
PAUSED = False

# Constants for data subscriptions
freq_64 = 15.625
freq_32 = freq_64 * 2.0
freq_4  = 250

Acc_X = 100
Acc_Y = 200
Acc_Z = 300

BVP  = 400
IBI  = 500
GSR  = 600
TEMP = 700
HR   = 800
BAT  = 900
TAG  = 1000


class 

# Helper function to generate timestamps in EE4 format
def now():
    return datetime.now().timestamp()

def cmd_handler(command):
    t = command.split()
    if t == []:
        return ""
    cmd = t[0].strip()
    args = command.split()[1:]
    
    if(cmd == "device_list"):
        return "R device_list 2 | 9ff167 Empatica_E4 | 7a3166 Empatica_E4\n"
    elif(cmd == "device_connect"):
        # TODO: add more behavior
        return "R device_connect OK\n"
    elif(cmd == "device_subscribe"):
        #TODO: add class for subscribed streams
        return "R " + command.strip() + " OK\n"
    elif(cmd == "pause_on"):
		
    else:
        return cmd

async def ee4_srv(r,w):
    while True:
        msg_raw = await r.read(100)
        
        try:
            msg = msg_raw.decode()
            w.write(cmd_handler(msg).encode())
        except UnicodeDecodeError:
            print("invalid char sent")

        await w.drain()

    w.close()

async def main():
    srv = await asyncio.start_server(ee4_srv, '127.0.0.1', 28000)
    print("srv start:", now())

    try:
        async with srv:
            await srv.serve_forever()
    except KeyboardInterrupt:
        exit(0)

if (__name__ == "__main__"):
    asyncio.run(main())

