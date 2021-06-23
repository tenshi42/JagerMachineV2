from ujson import dumps
from webserver import unknown_page
from controll import Controll
from machine import reset


class JagerController:
    def controller(self, pages, args):
        if pages[0] == "temperature":
            return dumps({'success': True, 'data': {'raw': Controll.get_instance().temps, 'mean': Controll.get_instance().mean_temps}})
        elif pages[0] == "status":
            c = Controll.get_instance()
            return dumps({'success': True, 'data': {
                'temperature': {
                    'raw': c.temps,
                    'mean': c.mean_temps,
                    'celsius': c.tempsCelsius
                },
                'isCooling': c.isCooling,
                'isCooled': c.isCooled,
                'isLiquidOk': c.isLiquidOk,
                'timeFromStart': c.time_from_start
            }})
        elif pages[0] == "reset":
            reset()
        elif pages[0] == "maintenance":
            if "set_maintenance_mode" in args:
                res = Controll.get_instance().set_maintenance_mode(int(args["set_maintenance_mode"]))
            elif "set_fan_state" in args:
                res = Controll.get_instance().set_fan_state(int(args["set_fan_state"]))
            elif "set_pump_state" in args:
                res = Controll.get_instance().set_pump_state(int(args["set_pump_state"]))
            elif "set_cooler_state" in args:
                res = Controll.get_instance().set_cooler_state(int(args["set_cooler_state"]))
            elif "set_valve_state" in args:
                res = Controll.get_instance().set_valve_state(int(args["set_valve_state"]))
            else:
                return dumps({
                    'success': False
                })

            return dumps({
                'success': True,
                'state': res
            })
        else:
            return unknown_page()
