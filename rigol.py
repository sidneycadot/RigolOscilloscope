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

class RigolOscilloscope:

    def __init__(self, device, verbosity = 0):

        self._verbosity = verbosity

        self._device = device

        self._device.flush()

    def setVerbosity(self, value):

        self._verbosity = value

    def getVerbosity(self):

        return self._verbosity

    def close(self):

        assert self._device is not None

        self._device.close()
        self._device = None

    #def readline(self):
    #    assert self._device is not None
    #    s = ""
    #    while True:
    #        c = os.read(self._device, 1)
    #        assert len(c) == 1
    #        if c == '\n':
    #            return s
    #        s += c

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

    #def info(self):

    #    old_verbosity = self.get_verbosity()
    #
    #    self.set_verbosity(0)
    #
    #    print "identify ............................ :", self.general_identify_query()
    #    print
    #    print "acquire:type ........................ :", self.acquire_type_query()
    #    print "acquire:mode ........................ :", self.acquire_mode_query()
    #    print "acquire:averages .................... :", self.acquire_averages_query()
    #    print "acquire:samplingrate (CH1) .......... :", self.acquire_samplingrate_query("CHANNEL1")
    #    print "acquire:samplingrate (CH2) .......... :", self.acquire_samplingrate_query("CHANNEL2")
    #    print "acquire:samplingrate (DIGITAL) ...... :", self.acquire_samplingrate_query("DIGITAL")
    #    print "acquire:memdepth .................... :", self.acquire_memdepth_query()
    #    print
    #    print "display:type ........................ :", self.display_type_query()
    #    print "display:grid ........................ :", self.display_grid_query()
    #    print "display:persist ..................... :", self.display_persist_query()
    #    print "display:menudisplay ................. :", self.display_menudisplay_query()
    #    print "display:menustatus .................. :", self.display_menustatus_query()
    #    print "display:brightness (grid) ........... :", self.display_brightness_query()
    #    print "display:intensity (waveform) ........ :", self.display_intensity_query()
    #    print
    #    print "timebase:mode ....................... :", self.timebase_mode_query()
    #    print "timebase:offset...................... :", self.timebase_offset_query(delayed = False)
    #    print "timebase:scale....................... :", self.timebase_scale_query(delayed = False)
    #    print "timebase:delayed:offset.............. :", self.timebase_offset_query(delayed = True)
    #    print "timebase:delayed:scale............... :", self.timebase_scale_query(delayed = True)
    #    print "timebase:format ..................... :", self.timebase_format_query()
    #    print
    #    print "waveform:points:mode ................ :", self.waveform_points_mode_query()
    #
    #    self.set_verbosity(old_verbosity)

    # General (a.k.a. IEEE) commands

    def getIdentity(self):

        """Identify the oscilloscope."""

        return self._execute("*IDN?", True)

    def cmdReset(self):

        """Perform a full reset of the oscilloscope."""

        return self._execute("*RST", False)

    # SYSTEM commands

    def cmdSystemRun(self):

        return self._execute(":SYSTEM:RUN", False)

    def cmdSystemStop(self):

        #assert False # Appears defunct
        return self._execute(":SYSTEM:STOP", False)

    def cmdSystemAuto(self):

        assert False # Appears defunct
        return self._execute(":SYSTEM:AUTO", False)

    def cmdSystemHardcopy(self):

        return self._execute(":SYSTEM:HARDCOPY", False)

    # ACQUIRE commands

    def setAcquireType(self, value):

        assert value in ["NORMAL", "AVERAGE", "PEAKDETECT"]

        response = self._execute(":ACQUIRE:TYPE " + value, False)

        return response

    def getAcquireType(self):

        response = self._execute(":ACQUIRE:TYPE?", True)

        assert response in ["NORMAL", "AVERAGE", "Peak Detect"]

        return response

    def setAcquireMode(self, value):

        assert value in ["RTIME", "ETIME"]

        response = self._execute(":ACQUIRE:MODE " + value, False)

        return response

    def getAcquireMode(self):

        response = self._execute(":ACQUIRE:MODE?", True)

        assert response in ["REAL_TIME", "EQUAL_TIME"]

        return response

    def setAcquireAverages(self, value):

        assert value in [2, 4, 8, 16, 32, 64, 128, 256]

        response = self._execute(":ACQUIRE:AVERAGES " + str(value), False)

        return response

    def getAcquireAverages(self):

        response = self._execute(":ACQUIRE:AVERAGES?", True)

        response = int(response)

        assert response in [2, 4, 8, 16, 32, 64, 128, 256]

        return response

    def getAcquireSamplingRate(self, channel):

        assert channel in ["CHANNEL1", "CHANNEL2", "DIGITAL"]

        response = self._execute(":ACQUIRE:SAMPLINGRATE? " + channel, True)

        response = float(response)

        return response

    def setAcquireMemDepth(self, value):

        assert value in ["NORMAL", "LONG"]

        response = self._execute(":ACQUIRE:MEMDEPTH " + value, False)

        return response

    def getAcquireMemDepth(self):

        response = self._execute(":ACQUIRE:MEMDEPTH?", True)

        assert response in ["NORMAL", "LONG"]

        return response

    # DISPLAY commands

    def setDisplayType(self, value):

        assert value in ["VECTORS", "DOTS"]

        response = self._execute(":DISPLAY:TYPE " + value, False)

        return response

    def getDisplayType(self):

        response = self._execute(":DISPLAY:TYPE?", True)

        assert response in ["VECTORS", "DOTS"]

        return response

    def setDisplayGrid(self, value):

        assert value in ["FULL", "HALF", "NONE"]

        response = self._execute(":DISPLAY:GRID " + value, False)

        return response

    def getDisplayGrid(self):

        response = self._execute(":DISPLAY:GRID?", True)

        assert response in ["FULL", "HALF", "NONE"]

        return response

    def setDisplayPersist(self, value):

        assert value in ["ON", "OFF"]

        response = self._execute(":DISPLAY:PERSIST " + value, False)

        return response

    def getDisplayPersist(self):

        response = self._execute(":DISPLAY:PERSIST?", True)

        assert response in ["ON", "OFF"]

        return response

    def setDisplayMenuDisplay(self, value):

        assert value in ["1s", "1s", "2s", "5s", "10s", "20s", "Infinite"]

        response = self._execute(":DISPLAY:MNUDISPLAY " + str(value), False)

        return response

    def getDisplayMenuDisplay(self):

        response = self._execute(":DISPLAY:MNUDISPLAY?", True)

        assert response in ["1s", "1s", "2s", "5s", "10s", "20s", "Infinite"]

        return response

    def setDisplayMenuStatus(self, value):

        assert value in ["ON", "OFF"]

        response = self._execute(":DISPLAY:MNUSTATUS " + value, False)

        return response

    def getDisplayMenuStatus(self):

        response = self._execute(":DISPLAY:MNUSTATUS?", True)

        assert response in  ["ON", "OFF"]

        return response

    def cmdDisplayClear(self):

        """Clear the display in persistent mode."""

        response = self._execute(":DISPLAY:CLEAR", False)

        return response

    def setDisplayBrightness(self, value):

        """Brightness of the grid."""

        assert isinstance(value, int) and (0 <= value <= 32)

        response = self._execute(":DISPLAY:BRIGHTNESS " + str(value), False)

        return response

    def getDisplayBrightness(self):

        response = self._execute(":DISPLAY:BRIGHTNESS?", True)

        response = int(response)

        assert (0 <= response <= 32)

        return response

    def setDisplayIntensity(self, value):

        """Intensity of the waveform(s)."""

        assert isinstance(value, int) and (0 <= value <= 32)

        response = self._execute(":DISPLAY:INTENSITY " + str(value), False)

        return response

    def getDisplayIntensity(self):

        response = self._execute(":DISPLAY:INTENSITY?", True)

        response = int(response)

        assert (0 <= response <= 32)

        return response

    ### TIMEBASE commands

    def getTimebaseMode(self, value):

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

    def cmdBeepAction(self):

        return self._execute(":BEEP:ACTION", False)

if __name__ == "__main__":
    main()
