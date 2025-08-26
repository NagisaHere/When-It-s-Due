import multiprocessing
import socket
import fcntl # huh
import struct

"""
def get_ip_address(ifname):
    s = socket.socket()
    # for control over open files, IO control
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915, # SIOCGIFADDR ; only AF_INET addresses
        struct.pack('256s', bytes(ifname[:15], 'utf-8'))
    )[20:24])

ip_address = get_ip_address()
"""
# ^ only if we want to connect on one address, but for simplicity sake

bind = "0.0.0.0:80"
workers = multiprocessing.cpu_count() * 2 + 1 # 2t + 1 for load balancing

timeout = 2
preload = True
