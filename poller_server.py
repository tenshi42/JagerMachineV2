import utime
import urequests
import ujson
import gc
from controll import Controll


class PollerServer:
    def __init__(self, poll_url):
        self.poll_url = poll_url

    def main_loop(self):
        urequests.get(self.poll_url + '/clear')
        utime.sleep(2)
        while True:
            try:
                r = urequests.get(self.poll_url + '/get_cmd')
                if r.status_code != 200:
                    print("Can't join server !")
                    utime.sleep(5)
                    continue
                else:
                    cmd = r.json()
                    if cmd['success']:
                        cmd = cmd["cmd"]

                        #print("doing : ", str(cmd))
                        self.threat(cmd)

                    utime.sleep(1)
            except Exception as e:
                print(e)
                utime.sleep(1)
            gc.collect()

            try:
                c = Controll.get_instance()
                state = {
                    'temperature': {
                        'raw': c.temps,
                        'mean': c.mean_temps,
                        'celsius': c.tempsCelsius
                    },
                    'isCooling': c.isCooling,
                    'isCooled': c.isCooled,
                    'isLiquidOk': c.isLiquidOk,
                    'timeFromStart': c.time_from_start
                }
                urequests.post(self.poll_url + '/set_state', data=ujson.dumps(state))
                utime.sleep(1)
            except Exception as e:
                print(e)
                utime.sleep(1)
            gc.collect()

    def threat(self, cmd_line):
        cmd = cmd_line['cmd']
        if cmd == 'serve':
            quantities = cmd_line['data']['quantities']
            Controll.get_instance().serve_jager(quantities)
            #print('serve quantities : ', str(quantities))
            return True
        elif cmd == 'temperature':
            print('temperature is unavailable at this time !')
            return True
        else:
            return False
