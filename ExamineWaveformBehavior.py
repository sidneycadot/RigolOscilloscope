#! /usr/bin/env python

import os, serial, rigol, time

def read_data(device):
    header =  device.read(10)
    count = int(header[2:])
    check_header = "#8%08d" % count
    assert header == check_header
    data = device.read(count)
    footer = device.read(1)
    assert footer == "\n"
    return data

def main():

    if True:
        device = serial.Serial("/dev/ttyUSB0", 38400, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, timeout = 5)
    else:
        device = os.fdopen(os.open("/dev/usbtmc0", os.O_RDWR), "rw")

    scope = rigol.RigolOscilloscope(device, verbosity = 1)

    for mode in ["NORMAL", "RAW", "MAX"]:

        scope._execute(":WAVEFORM:POINTS:MODE %s" % mode, False)

        readback = scope._execute(":WAVEFORM:POINTS:MODE?", True)
        print "@", readback

        for source in ["CHANNEL1", "CHANNEL2", "DIGITAL", "MATH", "FFT"]:
            scope._device.write(":WAVEFORM:DATA? %s\n" % source)
            data = read_data(scope._device)
            print mode, source, len(data)

    scope.close()

if __name__ == "__main__":
    main()
