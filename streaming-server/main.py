#!/usr/bin/env python3

import asyncio

from datetime import datetime

# Global to handle pause
PAUSED = False
CONNECTED = False

STREAM_TYPES = ["acc", "bvp", "gsr", "ibi", "tmp", "bat", "tag", "hr"]

# Constants for data subscriptions
freq_64 = 15.625 / 1000.0
freq_32 = freq_64 * 2.0
freq_4  = 250 / 1000.0

class Subscription:
    enabled = False
    freq = 0
    label = ""
    type = ""
    value = 0
    last_send = 0

    def __init__(self, l, t, fr, val):
        self.freq = fr
        self.label = l
        self.value = val
        self.type = t

    def send(self):
        # TODO: remove dummy print
        print("DUMMY PRINT")

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False


class Subscriptions_Holder:
    streams = [Subscription("E4_Acc", "acc", freq_32, [100, 200, 300]),
    Subscription("E4_Bvp", "bvp", freq_64, 400),
    Subscription("E4_Ibi", "ibi", 0, 500),
    Subscription("E4_Gsr", "gsr", freq_4,  600),
    Subscription("E4_Temperature", "tmp", freq_4, 700),
    Subscription("E4_Hr", "hr", 0, 800),
    Subscription("E4_Bat", "bat", 0, 1.0),
    Subscription("E4_Tag", "tag", 0, 1000)]

    def enable(self, t):
        for i in self.streams:
            if i.type == t or i.type == t.lower():
                i.enable()

    def disable(self, t):
        for i in self.streams:
            if i.type == t or i.type == t.lower():
                i.disable()

    def send_enabled(self):
        payload = []

        for i in self.streams:
            if i.enabled and not PAUSED:
                payload.append()

STREAMS = Subscriptions_Holder()

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
        for stream in STREAM_TYPES:
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

