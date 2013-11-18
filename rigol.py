#! /usr/bin/env python

import random, time, os
import serial, math, sys

# Web pages:
#
# http://hackaday.com/2012/03/30/grabbing-data-from-a-rigol-scope-with-python/
# http://www.cibomahto.com/2010/04/controlling-a-rigol-oscilloscope-using-linux-and-python/


# General
#
#     *IDN?
#     *RST
#
# SYSTEM
#
#     :SYSTEM:RUN
#     :SYSTEM:STOP
#     :SYSTEM:AUTO
#     :SYSTEM:HARDCOPY
#
# ACQUIRE
#
#     :ACQUIRE:TYPE                   query, or ( NORMAL | AVERAGE | PEAKDETECT )
#     :ACQUIRE:MODE                   query, or (REAL_TIME or EQUAL_TIME)
#     :ACQUIRE:AVERAGES               query, or (2, 4, 8, 16, 32, 64, 128, 256)
#     :ACQUIRE:SAMPINTEGRATE          query, or ( CHANNEL1 | CHANNEL2 | DIGITAL )
#     :ACQUIRE:MEMDEPTH               query, or ( LONG | NORMAL )
#
# DISPLAY
#
# TIMEBASE
#
# TRIGGER
#
# STORAGE
#
# MATH
#
# CHANNEL
#
# MEASURE
#
# WAVEFORM
#
# LA
#
# KEY
#
# Other

def usbtmc(device):
    fd = os.open(device, os.O_RDWR)
    return os.fdopen(fd, "rw")

class RigolOscilloscope:

    def __init__(self, device):

        self._verbosity = 1

        #self._device = serial.Serial (
        #        port             = serial_port,
        #        baudrate         = baudrate,
        #        bytesize         = serial.EIGHTBITS,
        #        parity           = serial.PARITY_NONE,
        #        stopbits         = serial.STOPBITS_ONE,
        #        timeout          = 5,
        #        xonxoff          = False,
        #        rtscts           = False,
        #        writeTimeout     = False,
        #        dsrdtr           = False,
        #        interCharTimeout = None
        #    )

        self._device = device

    def set_verbosity(self, value):

        self._verbosity = value

    def get_verbosity(self):

        return self._verbosity

    def close(self):

        assert self._device is not None

        self._device.close()
        self._device = None

    def readline(self):
        assert self._device is not None
        s = ""
        while True:
            c = os.read(self._device, 1)
            assert len(c) == 1
            if c == '\n':
                return s
            s += c

    def __del__(self):

        if self._device is not None:
            self.close()

    def _execute(self, cmd, expect_response):

        assert self._device is not None

        if self._verbosity > 0:
            print "[serial-out] <%s>" % cmd

        self._device.write(cmd + "\n")
        self._device.flush()

        if expect_response:
            response = self._device.readline()

            assert response.endswith("\n")
            response = response[:-1]

            if self._verbosity > 1:
                print "[serial-in ] <%s>" % [ord(c) for c in response]
            if self._verbosity > 0:
                print "[serial-in ] <%s>" % response
        else:
            response = None

        return response

    def info(self):

        old_verbosity = self.get_verbosity()

        self.set_verbosity(0)

        print "identify ............................ :", self.general_identify_query()
        print
        print "acquire:type ........................ :", self.acquire_type_query()
        print "acquire:mode ........................ :", self.acquire_mode_query()
        print "acquire:averages .................... :", self.acquire_averages_query()
        print "acquire:samplingrate (CH1) .......... :", self.acquire_samplingrate_query("CHANNEL1")
        print "acquire:samplingrate (CH2) .......... :", self.acquire_samplingrate_query("CHANNEL2")
        print "acquire:samplingrate (DIGITAL) ...... :", self.acquire_samplingrate_query("DIGITAL")
        print "acquire:memdepth .................... :", self.acquire_memdepth_query()
        print
        print "display:type ........................ :", self.display_type_query()
        print "display:grid ........................ :", self.display_grid_query()
        print "display:persist ..................... :", self.display_persist_query()
        print "display:menudisplay ................. :", self.display_menudisplay_query()
        print "display:menustatus .................. :", self.display_menustatus_query()
        print "display:brightness (grid) ........... :", self.display_brightness_query()
        print "display:intensity (waveform) ........ :", self.display_intensity_query()
        print
        print "timebase:mode ....................... :", self.timebase_mode_query()
        print "timebase:offset...................... :", self.timebase_offset_query(delayed = False)
        print "timebase:scale....................... :", self.timebase_scale_query(delayed = False)
        print "timebase:delayed:offset.............. :", self.timebase_offset_query(delayed = True)
        print "timebase:delayed:scale............... :", self.timebase_scale_query(delayed = True)
        print "timebase:format ..................... :", self.timebase_format_query()
        print
        print "waveform:points:mode ................ :", self.waveform_points_mode_query()

        self.set_verbosity(old_verbosity)

    ### General (a.k.a. IEEE) commands

    def general_identify_query(self):

        """Identify the oscilloscope."""

        return self._execute("*IDN?", True)

    def general_reset_command(self):

        """Perform a full reset of the oscilloscope."""

        return self._execute("*RST", False)

    ### SYSTEM commands

    def system_run_command(self):

        return self._execute(":SYSTEM:RUN", False)

    def system_stop_command(self):

        #assert False # Appears defunct
        return self._execute(":SYSTEM:STOP", False)

    def system_auto_command(self):

        assert False # Appears defunct
        return self._execute(":SYSTEM:AUTO", False)

    def system_hardcopy_command(self):

        return self._execute(":SYSTEM:HARDCOPY", False)

    ### ACQUIRE commands

    def acquire_type_set(self, value):

        assert value in ["NORMAL", "AVERAGE", "PEAKDETECT"]

        response = self._execute(":ACQUIRE:TYPE " + value, False)

        return response

    def acquire_type_query(self):

        response = self._execute(":ACQUIRE:TYPE?", True)

        assert response in ["NORMAL", "AVERAGE", "Peak Detect"]

        return response

    def acquire_mode_set(self, value):

        assert value in ["RTIME", "ETIME"]

        response = self._execute(":ACQUIRE:MODE " + value, False)

        return response

    def acquire_mode_query(self):

        response = self._execute(":ACQUIRE:MODE?", True)

        assert response in ["REAL_TIME", "EQUAL_TIME"]

        return response

    def acquire_averages_set(self, value):

        assert value in [2, 4, 8, 16, 32, 64, 128, 256]

        response = self._execute(":ACQUIRE:AVERAGES " + str(value), False)

        return response

    def acquire_averages_query(self):

        response = self._execute(":ACQUIRE:AVERAGES?", True)

        response = int(response)

        assert response in [2, 4, 8, 16, 32, 64, 128, 256]

        return response

    def acquire_samplingrate_query(self, channel):

        assert channel in ["CHANNEL1", "CHANNEL2", "DIGITAL"]

        response = self._execute(":ACQUIRE:SAMPLINGRATE? " + channel, True)

        response = float(response)

        return response

    def acquire_memdepth_set(self, value):

        assert value in ["NORMAL", "LONG"]

        response = self._execute(":ACQUIRE:MEMDEPTH " + value, False)

        return response

    def acquire_memdepth_query(self):

        response = self._execute(":ACQUIRE:MEMDEPTH?", True)

        assert response in ["NORMAL", "LONG"]

        return response

    ### DISPLAY commands

    def display_type_set(self, value):

        assert value in ["VECTORS", "DOTS"]

        response = self._execute(":DISPLAY:TYPE " + value, False)

        return response

    def display_type_query(self):

        response = self._execute(":DISPLAY:TYPE?", True)

        assert response in ["VECTORS", "DOTS"]

        return response

    def display_grid_set(self, value):

        assert value in ["FULL", "HALF", "NONE"]

        response = self._execute(":DISPLAY:GRID " + value, False)

        return response

    def display_grid_query(self):

        response = self._execute(":DISPLAY:GRID?", True)

        assert response in ["FULL", "HALF", "NONE"]

        return response

    def display_persist_set(self, value):

        assert value in ["ON", "OFF"]

        response = self._execute(":DISPLAY:PERSIST " + value, False)

        return response

    def display_persist_query(self):

        response = self._execute(":DISPLAY:PERSIST?", True)

        assert response in ["ON", "OFF"]

        return response

    def display_menudisplay_set(self, value):

        assert value in ["1s", "1s", "2s", "5s", "10s", "20s", "INFINITE"]

        response = self._execute(":DISPLAY:MNUDISPLAY " + str(value), False)

        return response

    def display_menudisplay_query(self):

        response = self._execute(":DISPLAY:MNUDISPLAY?", True)

        assert response in ["1s", "1s", "2s", "5s", "10s", "20s", "Infinite"]

        return response

    def display_menustatus_set(self, value):

        assert value in ["ON", "OFF"]

        response = self._execute(":DISPLAY:MNUSTATUS " + value, False)

        return response

    def display_menustatus_query(self):

        response = self._execute(":DISPLAY:MNUSTATUS?", True)

        assert response in  ["ON", "OFF"]

        return response

    def display_clear_command(self):

        response = self._execute(":DISPLAY:CLEAR", False)

        return response

    def display_brightness_set(self, value):

        assert isinstance(value, int) and (0 <= value <= 32)

        response = self._execute(":DISPLAY:BRIGHTNESS " + str(value), False)

        return response

    def display_brightness_query(self):

        response = self._execute(":DISPLAY:BRIGHTNESS?", True)

        response = int(response)

        assert (0 <= response <= 32)

        return response

    def display_intensity_set(self, value):

        assert isinstance(value, int) and (0 <= value <= 32)

        response = self._execute(":DISPLAY:INTENSITY " + str(value), False)

        return response

    def display_intensity_query(self):

        response = self._execute(":DISPLAY:INTENSITY?", True)

        response = int(response)

        assert (0 <= response <= 32)

        return response

    ### TIMEBASE commands

    def timebase_mode_set(self, value):

        assert value in ["MAIN", "DELAYED"]

        response = self._execute(":TIMEBASE:MODE " + value, False)

        return response

    def timebase_mode_query(self):

        response = self._execute(":TIMEBASE:MODE?", True)

        assert response in ["MAIN", "DELAYED"]

        return response

    def timebase_offset_set(self, delayed, value):

        if delayed:
            response = self._execute(":TIMEBASE:DELAYED:OFFSET " + str(value), False)
        else:
            response = self._execute(":TIMEBASE:OFFSET " + str(value), False)

        return response

    def timebase_offset_query(self, delayed):

        if delayed:
            response = self._execute(":TIMEBASE:DELAYED:OFFSET?", True)
        else:
            response = self._execute(":TIMEBASE:OFFSET?", True)

        response = float(response)

        return response

    def timebaseSetScale(self, value, delayed = False):

        if delayed:
            response = self._execute(":TIMEBASE:DELAYED:SCALE " + str(value), False)
        else:
            response = self._execute(":TIMEBASE:SCALE " + str(value), False)

        return response

    def timebaseGetScale(self, delayed = False):

        if delayed:
            response = self._execute(":TIMEBASE:DELAYED:SCALE?", True)
        else:
            response = self._execute(":TIMEBASE:SCALE?", True)

        response = float(response)

        return response

    def timebase_format_set(self, value):

        assert value in ["XY", "YT", "SCANNING"]

        response = self._execute(":TIMEBASE:FORMAT " + value, False)

        return response

    def timebase_format_query(self):

        response = self._execute(":TIMEBASE:FORMAT?", True)

        assert response in ["X-Y", "Y-T", "SCANNING"]

        return response

    def timebase_format_set(self, value):

        assert value in ["XY", "YT", "SCANNING"]

        response = self._execute(":TIMEBASE:FORMAT " + value, False)

        return response

    ### TRIGGER commands

    ### STORAGE commands

    def storage_factory_load_command(self):

        response = self._execute(":STORAGE:FACTORY:LOAD", False)

        return response

    ### MATH commands

    ### CHANNEL commands

    def channel_bandwidth_limit_set(self, channel, value):

        assert channel in [1, 2]
        assert value in ["ON", "OFF"]

        response = self._execute(":CHANNEL" + str(channel) +":BWLIMIT " + value, False)

        return response

    def channel_bandwidth_limit_query(self, channel, value):

        response = self._execute(":CHANNEL" + str(channel) + ":BWLIMIT?", True)

        assert response in ["X-Y", "Y-T", "SCANNING"]

        return response

    ### MEASURE commands

    def measurePositiveEdgeDelay(self):

        response = self._execute(":MEASURE:PDELAY?", True)

        return response

    ### KEY commands

    def keyGetLock(self):

        response = self._execute(":KEY:LOCK?", True)
        #assert response in []
        return response

    def keyPushAuto(self):

        return self._execute(":KEY:AUTO", False)

    def keyPushForce(self):

        return self._execute(":KEY:FORCE", False)

    ### Waveform commands

    def read_data(self):

        response = self._device.read(10)
        assert len(response) == 10
        assert response.startswith("#8")
        print "DATASPEC: <%s>" % response

        num_samples = int(response[3:])

        #check = "#" + str(800000000 + num_samples)
        #assert check == response

        print "reading", num_samples, "samples ..."
        response = self._device.read(num_samples)

        data = map(ord, response)

        response = self._device.read(1)
        print "END-OF-DATA:", [ord(x) for x in response]
        assert response == "\n"

        return data

    def waveform_data_query(self, source):

        assert self._device is not None

        assert source in ["CHANNEL1", "CHANNEL2", "DIGITAL", "MATH", "FFT"]

        self._device.write(":WAVEFORM:DATA? " + source + "\n")

        data = self.read_data()

        data2 = self.read_data()
        data3 = self.read_data()
        data4 = self.read_data()

    def waveform_points_mode_set(self, mode):

        assert mode in ["NORMAL", "MAXIMUM", "RAW"]

        response = self._execute(":WAVEFORM:POINTS:MODE " + mode, False)

        return response

    def waveform_points_mode_query(self):

        response = self._execute(":WAVEFORM:POINTS:MODE?", True)

        assert response in ["NORMAL", "MAXIMUM", "RAW"]

        return response

    ### Other commands

    def beep_action(self):

        return self._execute(":BEEP:ACTION", False)

def old():

    rigol.storage_factory_load_command()

    #rigol.info()

    if False:
        rigol_id = rigol.general_identify_query()
        print "*** IDENTIFICATION:", rigol_id

        for i in xrange(33):
            options = ["XY", "YT", "SCANNING"]
            value = options[i % len(options)]
            #value = i
            rigol.timebase_format_set(value)
            value_queried = rigol.timebase_format_query()
            print value, value_queried
            time.sleep(5)

    #rigol.waveform_points_mode_set("RAW")
    #print rigol.waveform_points_mode_query()
    rigol.info()

    if False:

        for i in range(1):
            rigol.system_stop()
            data = rigol.waveform_data_query("CHANNEL1")
            f = open("data.txt", "w")
            for i in data:
                print >> f, i
            f.close()

    # Back to manual mode
    rigol.key_force()

possible_div_settings = [
              2.000e-9, 5.000e-9,
    10.00e-9, 20.00e-9, 50.00e-9,
    100.0e-9, 200.0e-9, 500.0e-9,
    1.000e-6, 2.000e-6, 5.000e-6,
    10.00e-6, 20.00e-6, 50.00e-6,
    100.0e-6, 200.0e-6, 500.0e-6,
    1.000e-3, 2.000e-3, 5.000e-3,
    10.00e-3, 20.00e-3, 50.00e-3,
    100.0e-3, 200.0e-3, 500.0e-3,
    1.000e+0, 2.000e+0, 5.000e+0,
    10.00e+0, 20.00e+0, 50.00e+0 ]

def main():

    if False:
        device = usbtmc("/dev/usbtmc0")
    else:
        device = serial.Serial("/dev/ttyUSB0", 9600, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, timeout = 5)

    rigol = RigolOscilloscope(device)

    rigol._verbosity = 0

    #print rigol.general_identify_query()

    t_start = time.time()
    t_offset = math.floor(t_start / 86400.0) * 86400.0 - 3600.0

    while True:

        skip = 0
        while True:
            t1 = time.time()
            t1_int = math.floor(t1)
            t1_frac = t1 - t1_int
            if 0.500 <= t1_frac <= 0.600:
                msm = rigol.measurePositiveEdgeDelay()

                t = (t1_int - t_offset) / 3600.0

                try:
                    delay = float(msm)
                    if delay > 1.0:
                        raise ValueError
                except ValueError:
                    delay = float("NaN")

                print "time %15.9f delay %15.9f" % (t, delay * 1e6)

                time.sleep(0.900)
                skip = 0
            else:
                time.sleep(0.010)
                skip += 1

    rigol.key_force()

    rigol.close()

if __name__ == "__main__":
    main()
