def to_signed(x):
    if x > 127:
        return (256-x)*(-1)
    else:
        return x

class Instrument(object):
    def __init__(self, instr_id, interface):
        self.interface = interface
        self.instr_id = instr_id


class Multimeter(Instrument):
    def read_dc_volts(self):
        raise NotImplemented()

    def read_ac_volts(self):
        raise NotImplemented()

    def read_resistance(self):
        raise NotImplemented()

    def read_dc_current(self):
        raise NotImplemented()

    def read_ac_current(self):
        raise NotImplemented()


class PowerSupply(Instrument):
    def set_voltage(self, channel, voltage):
        raise NotImplemented()

    def get_voltage(self, channel):
        raise NotImplemented()


class Oscilloscope(Instrument):
    pass


class DM3058(Multimeter):
    def read_dc_volts(self):
        return float(self.interface.query(self.instr_id, "MEAS:VOLT:DC?"))

    def read_ac_volts(self):
        return float(self.interface.query(self.instr_id, "MEAS:VOLT:AC?"))

    def read_resistance(self):
        raise NotImplemented()

    def read_dc_current(self):
        raise NotImplemented()

    def read_ac_current(self):
        raise NotImplemented()

class DP800(PowerSupply):
    def set_voltage(self, channel, voltage):
        self.interface.write(self.instr_id, "SOUR%d:VOLT %f" % (channel, voltage))

    def set_current(self, channel, current):
        self.interface.write(self.instr_id, "SOUR%d:CURR %f" % (channel, current))

    def get_set_voltage(self, channel, voltage):
        return float(self.interface.query(self.instr_id, "SOUR%d:VOLT?" % channel))

    def get_set_current(self, channel, current):
        return float(self.interface.query(self.instr_id, "SOUR%d:CURR?" % channel))

    def get_measured_voltage(self, channel):
        return float(self.interface.query(self.instr_id, "MEAS:VOLT? CH%d" % channel))

    def get_measured_current(self, channel):
        return float(self.interface.query(self.instr_id, "MEAS:CURR? CH%d" % channel))

    def get_measured_power(self, channel):
        return float(self.interface.query(self.instr_id, "MEAS:POWER? CH%d" % channel))

    def enable_channel(self, channel):
        self.interface.write(self.instr_id, "OUTP CH%d,ON" % channel)

    def disable_channel(self, channel):
        self.interface.write(self.instr_id, "OUTP CH%d,OFF" % channel)

class DSO2000(Oscilloscope):
    def set_timebase(self, time_per_div):
        #10ns/div = 100ns/window
        #ns = -9
        time_per_10_div = time_per_div*10
        time_string = "%.2E" % time_per_10_div
        self.timebase = time_per_10_div
        self.interface.write(self.instr_id, ":TIM:RANG %s" % time_string)

    def set_range(self, channel, full_scale_range):
        self.full_scale_range = full_scale_range
        self.interface.write(self.instr_id, ":CHAN%d:RANG %d" % (channel, full_scale_range))

    def enable_averaging(self, count=None):
        self.interface.write(self.instr_id, ":ACQ:TYPE AVER")
        if count != None:
            self.interface.write(self.instr_id, ":ACQ:COUNT %d" % count)

    def select_channel(self, channel):
        self.interface.write(self.instr_id, ":WAV:SOUR CHAN%d" % channel)

    def set_waveform_data_params(self):
        self.resolution = 256
        self.interface.write(self.instr_id, ":WAV:FORM BYTE")
        self.interface.write(self.instr_id, ":WAV:UNS 0")
        self.interface.write(self.instr_id, ":WAV:POINTS 1000")

    def get_waveform(self):
        lsb = float(self.full_scale_range)/float(self.resolution)
        wave_data = self.interface.query_binary(self.instr_id, "WAV:DATA?")
        return [lsb*float(to_signed(x)) for x in wave_data]
