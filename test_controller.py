from ujson import dumps
from webserver import unknown_page


class TestController:
    def controller(self, pages, args):
        if pages[0] == "sub_test":
            return dumps({'success': True, 'message': 'Sub test !', 'args': str(args)})
        else:
            return unknown_page()
