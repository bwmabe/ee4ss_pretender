#!/usr/bin/env python3

import asyncio

from datetime import datetime

# Global to handle pause
PAUSED = False
CONNECTED = False

STREAMS = ["acc", "bvp", "gsr", "ibi", "tmp", "bat", "tag"]

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


class Subscription:
    enabled = False
    freq = 0
    label = ""
    value = 0

    def __init__(self, l, fr, val):
        self.freq = fr
        self.label = l
        self.value = val

    def send(self):
        # TODO: remove dummy print
        print("DUMMY PRINT")


def subscriptions():
    acc = Subscription("E4_Acc", freq_32, [100, 200, 300])
    bvp = Subscription("E4_Bvp", freq_64, 400)
    ibi = Subscription("E4_Ibi", 0, 500)
    gsr = Subscription("E4_Gsr", freq_4,  600)
    tmp = Subscription("E4_Temperature", freq_4, 700)
    hr  = Subscription("E4_Hr", 0, 800)
    bat = Subscription("E4_Bat", 0, 1.0)
    tag = Subscription("E4_Tag", 0, 1000)



# Helper function to generate timestamps in EE4 format
def now():
    return datetime.now().timestamp()

def cmd_handler(command_raw):
    global PAUSED
    global CONNECTED
    global STREAMS

    # Empty string for testing
    s = ""

    # Temp variable
    t = command_raw.split()

    # If t does not exist, or command_raw empty, return empty
    if not t:
        return ""

    cmd = t[0].strip()
    args = command_raw.split()[1:]
    
    if(cmd == "device_list"):
        return "R device_list 2 | 9ff167 Empatica_E4 | 7a3166 Empatica_E4\n"
    elif(cmd == "device_connect"):
        # TODO: add more behavior
        CONNECTED = True
        return "R device_connect OK\n"
    elif(cmd == "device_subscribe"):
        #TODO: add class for subscribed streams
        # --IN PROGRESS--
        if len(args) > 2:
            return "R device_subscribe ERR too many arguments\n"
        for stream in STREAMS:
            if args[0] == stream or args[0] == stream.upper():
                return "R " + cmd + " " + s.join(args) + " OK\n"
    elif(cmd == "pause"):
        if len(args) > 1:
            return "R pause ERR too many arguments\n"
        else:
            if args[0] == "ON" or args[0] == "on":
                if PAUSED:
                    return "R pause ERR already paused\n"
                PAUSED = True
                return "R pause ON\n"
            elif args[0] == "OFF" or args[0] == "off":
                if not PAUSED:
                    return "R pause ERR not paused\n"
                PAUSED = False
                return "R pause OFF\n"
            else:
                return "R pause ERR wrong argument\n"

    else:
        # TODO: remove this
        print(cmd)
        return ""

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
    print("Server started!")

    try:
        async with srv:
            await srv.serve_forever()
    except KeyboardInterrupt:
        exit(0)

# For testing...
if (__name__ == "__main__"):
    # In try-except to suppress irrelevant errors
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit(0)

