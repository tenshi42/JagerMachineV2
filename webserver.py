try:
    import usocket as socket
except:
    import socket
from ujson import dumps
from machine import reset
import utils
import gc


class WebServer:
    def __init__(self, ip: str, port: int):
        self.controllers = {}
        self.addr = socket.getaddrinfo(ip, port)[0][-1]
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(self.addr)
        self.s.listen(5)

    def main_loop(self):
        while True:
            cl, addr = self.s.accept()
            #print('client connected from', self.addr)
            req = str(cl.recv(1024))
            self.treat_request(req, cl)
            cl.close()

    def parse_request(self, req):
        #print(req)
        sub = req.split(" HTTP")[0].split('?')
        pages = sub[0].split('/')[1:]
        args = dict([x.split('=') for x in utils.unquote(sub[1]).decode("utf-8").split('&')] if len(sub) > 1 else [])
        return pages, args

    def treat_request(self, req, cl):
        req = str(req)
        #print(req)
        page, args = self.parse_request(req)
        #print("page : ", page)
        #print("args : ", args)
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        try:
            self.controller(page, args, cl)
        except Exception as e:
            print(e)
        cl.close()

    def controller(self, pages, args, cl):
        content = None
        if len(pages) > 1:
            cur_controller = pages[0]
            if cur_controller in self.controllers:
                content = self.controllers[cur_controller].controller(pages[1:], args)
        else:
            if len(pages) == 0:
                content = unknown_page()
            elif pages[0] == 'test':
                content = dumps({'success': True, 'message': 'test'})
            elif pages[0] == 'set_wifi':
                if 'pass' in args:
                    content = set_wifi_page()
                elif 'SSID' in args and 'password' in args:
                    save_wifi(args['SSID'], args['password'])
                    cl.send(dumps({'success': True, 'message': 'Wifi set !'}))
                    reset()
                else:
                    content = unknown_page()
            else:
                content = unknown_page()

        cl.send(content)
        gc.collect()

    def add_controller(self, name, controller):
        self.controllers[name] = controller


def save_wifi(SSID, password):
    d = {"network_name": SSID, "network_password": password}
    f = open("config.json", "w")
    f.write(dumps(d))
    f.close()


def set_wifi_page():
    return """
    <!doctype html>
    <html>
        <head>
            <title>Set Wifi</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta charset="utf8">
        </head>
        <body>
            <h2 class="title">Configure Wifi</h2>
            <form action="/set_wifi" method="get">
                SSID: <input class="input" type="text" name="SSID">
                Password: <input class="input" type="text" name="password">
                <input type="submit" value="Submit">
            </form>
        </body>
    </html>
    """


def unknown_page():
    return dumps({'success': False, 'message': '404 : unknown page'})