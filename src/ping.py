import ping3

PING_TOTAL = 4

def is_alive(ip: str):
    success = 0
    for i in range(PING_TOTAL):
        try:
            resp = ping3.ping(ip, timeout=1)
        except:
            resp = None
        if resp is not False and resp is not None:
            success += 1
    return success >= PING_TOTAL/2
