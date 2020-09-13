"""
DS3231 RTC driver

Inspired and adapted from:
https://github.com/micropython-Chinese-Community/mpy-lib/tree/master/misc/DS3231
"""
DS3231_I2C_ADDR = 0x68
DS3231_REG_SEC = 0x00
DS3231_REG_MIN = 0x01
DS3231_REG_HOUR = 0x02
DS3231_REG_WEEKDAY = 0x03
DS3231_REG_DAY = 0x04
DS3231_REG_MONTH = 0x05
DS3231_REG_YEAR = 0x06
DS3231_REG_CTRL = 0x0E
DS3231_REG_TEMP = 0x11


class DS3231:
    def __init__(self, i2c):
        self.i2c = i2c
        self.set_reg(DS3231_REG_CTRL, 0x4C)

    @staticmethod
    def dec_to_hex(data):
        return (data // 10) * 16 + (data % 10)

    @staticmethod
    def hex_to_dec(data):
        return (data // 16) * 10 + (data % 16)

    def set_reg(self, reg, data):
        self.i2c.writeto(DS3231_I2C_ADDR, bytearray([reg, data]))

    def get_reg(self, reg):
        self.i2c.writeto(DS3231_I2C_ADDR, bytearray([reg]))
        return self.i2c.readfrom(DS3231_I2C_ADDR, 1)[0]

    def second(self, second=None):
        if second is None:
            return self.hex_to_dec(self.get_reg(DS3231_REG_SEC))
        else:
            self.set_reg(DS3231_REG_SEC, self.dec_to_hex(second % 60))

    def minute(self, minute=None):
        if minute is None:
            return self.hex_to_dec(self.get_reg(DS3231_REG_MIN))
        else:
            self.set_reg(DS3231_REG_MIN, self.dec_to_hex(minute % 60))

    def hour(self, hour=None):
        if hour is None:
            return self.hex_to_dec(self.get_reg(DS3231_REG_HOUR))
        else:
            self.set_reg(DS3231_REG_HOUR, self.dec_to_hex(hour % 24))

    def weekday(self, weekday=None):
        if weekday is None:
            return self.hex_to_dec(self.get_reg(DS3231_REG_WEEKDAY))
        else:
            self.set_reg(DS3231_REG_WEEKDAY, self.dec_to_hex(weekday % 8))

    def day(self, day=None):
        if day is None:
            return self.hex_to_dec(self.get_reg(DS3231_REG_DAY))
        else:
            self.set_reg(DS3231_REG_DAY, self.dec_to_hex(day % 32))

    def month(self, month=None):
        if month is None:
            return self.hex_to_dec(self.get_reg(DS3231_REG_MONTH))
        else:
            self.set_reg(DS3231_REG_MONTH, self.dec_to_hex(month % 13))

    def year(self, year=None):
        if year is None:
            return self.hex_to_dec(self.get_reg(DS3231_REG_YEAR)) + 2000
        else:
            self.set_reg(DS3231_REG_YEAR, self.dec_to_hex(year % 100))

    def date(self, data=None):
        if data is None:
            return [self.year(), self.month(), self.day()]
        else:
            self.year(data[0] % 100)
            self.month(data[1] % 13)
            self.day(data[2] % 32)

    def time(self, data=None):
        if data is None:
            return [self.hour(), self.minute(), self.second()]
        else:
            self.hour(data[0] % 24)
            self.minute(data[1] % 60)
            self.second(data[2] % 60)

    def datetime(self, data=None):
        if data is None:
            return self.date() + [self.weekday()] + self.time()
        else:
            self.year(data[0])
            self.month(data[1])
            self.day(data[2])
            self.weekday(data[3])
            self.hour(data[4])
            self.minute(data[5])
            self.second(data[6])

    def temperature(self):
        t = self.get_reg(DS3231_REG_TEMP)
        t_high_precision = self.get_reg(DS3231_REG_TEMP + 1)
        if t > 0x7F:
            return t - t_high_precision / 256 - 256
        else:
            return t + t_high_precision / 256
