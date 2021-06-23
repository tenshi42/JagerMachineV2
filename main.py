try:
    import usocket as socket
except:
    import socket

import micropython
import gc
import _thread
import utime

from poller_server import PollerServer

from webserver import WebServer
from test_controller import TestController
from jager_controller import JagerController

from controll import Controll
from display import Display


print()
gc.collect()
micropython.mem_info()
print()


def flash_I():
    while True:
        Display.get_instance().I()
        utime.sleep_ms(500)
        Display.get_instance().off()
        utime.sleep_ms(500)


def main(is_connected, config):
    controll = Controll.get_instance()
    controll.init()

    ws = WebServer('0.0.0.0', 80)
    ws.add_controller('test', TestController())
    ws.add_controller('jager', JagerController())

    ps = PollerServer(config['poll_url'])

    _thread.start_new_thread(ws.main_loop, ())
    _thread.start_new_thread(ps.main_loop, ())
    if is_connected:
        _thread.start_new_thread(controll.main_loop, ())
    else:
        _thread.start_new_thread(flash_I, ())

    print("Ready !")
