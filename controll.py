from machine import Pin, ADC
import utime
from display import Display


class Controll:
    instance = None

    def __init__(self):
        self.valvePin = Pin(21, Pin.OUT)
        self.jagerPumpAPin = Pin(22, Pin.OUT)
        self.jagerPumpBPin = Pin(23, Pin.OUT)

        self.sensorPin = ADC(Pin(34))
        self.liquidPin = Pin(17, Pin.IN)
        self.coolerPin = Pin(18, Pin.OUT)
        self.fanPin = Pin(19, Pin.OUT)

        self.isFirstCooling = True
        self.isCooling = False
        self.isCooled = False
        self.isLiquidOk = False

        self.tempsHistory = []

        self.R1 = 10000
        self.logR2 = 0
        self.R2 = 0
        self.T = 0
        self.c1 = 1.009249522e-03
        self.c2 = 2.378405444e-04
        self.c3 = 2.019202697e-07

        self.time_from_start = 0
        self.fan_time = 0

        self.temps = 0
        self.tempsCelsius = 0
        self.mean_temps = 0

        self.maintenanceMode = False

    def set_maintenance_mode(self, v):
        self.maintenanceMode = v
        return v == 1

    def set_fan_state(self, state):
        if not self.maintenanceMode:
            return False
        self.fanPin.value(state)
        return True

    def set_cooler_state(self, state):
        if not self.maintenanceMode or not self.isLiquidOk:
            return False
        self.coolerPin.value(state)
        return True

    def set_pump_state(self, state):
        if not self.maintenanceMode:
            return False
        self.jagerPumpBPin.value(state)
        return True

    def set_valve_state(self, state):
        if not self.maintenanceMode:
            return False
        self.valvePin.value(state)
        return True

    @classmethod
    def get_instance(cls):
        if not Controll.instance:
            Controll.instance = Controll()
        return Controll.instance

    def init(self):
        self.sensorPin.atten(ADC.ATTN_11DB)
        self.sensorPin.width(ADC.WIDTH_10BIT)

        self.jagerPumpAPin.off()
        self.jagerPumpBPin.off()
        self.valvePin.off()
        self.coolerPin.off()
        self.fanPin.off()

    def serve_jager(self, quantities):
        #print('Serve : ', str(quantities))
        if quantities['jager'] > 0:
            self.valvePin.on()
            utime.sleep(quantities['jager'])
            self.valvePin.off()
        utime.sleep(2)
        if quantities['other'] > 0:
            self.jagerPumpBPin.on()
            utime.sleep(quantities['other'])
            self.jagerPumpBPin.off()
        utime.sleep(3)

    def controll(self, temps, isLiquidOk):
        if temps > 210 and not self.isCooling and not self.isCooled and isLiquidOk:
            self.fanPin.on()
            if self.isFirstCooling:
                if self.time_from_start < 180:
                    return
                self.isFirstCooling = False
            else:
                if self.fan_time > 30:
                    self.fan_time = 0
                if self.fan_time < 30:
                    return
            self.coolerPin.on()
            self.isCooling = True
            self.isCooled = False
        elif (temps <= 210 or not isLiquidOk) and self.isCooling and not self.isCooled:  # -15°C approximately
            self.fanPin.off()
            self.coolerPin.off()
            self.isCooling = False
            self.isCooled = True
        elif (temps >= 225 or not isLiquidOk) and self.isCooled:  # -14°C approximately
            self.isCooling = False
            self.isCooled = False

    def get_smooth_value(self, cur_val):
        if len(self.tempsHistory) == 10:
            self.tempsHistory.pop(0)
        self.tempsHistory.append(cur_val)

        if len(self.tempsHistory) < 10:
            return cur_val
        else:
            return int(sum(self.tempsHistory) / 10)

    def compute_celsius_temps(self, v):
        return 0.0956*v-36.4

    def main_loop(self):
        while True:
            utime.sleep(1)
            self.time_from_start += 1
            self.fan_time += 1

            self.isLiquidOk = self.liquidPin.value()
            self.temps = self.sensorPin.read()
            self.mean_temps = self.get_smooth_value(self.temps)
            self.tempsCelsius = self.compute_celsius_temps(self.mean_temps)

            if self.isCooling:
                Display.get_instance().cooling()

            if not self.isLiquidOk:
                Display.get_instance().L()

            if self.isLiquidOk and ((not self.isCooled and not self.isCooling) or (self.isCooling and self.isCooled)):
                Display.get_instance().F()

            if len(self.tempsHistory) == 10 and not self.maintenanceMode:
                self.controll(self.mean_temps, self.isLiquidOk)
