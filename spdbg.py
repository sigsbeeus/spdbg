#!/usr/local/bin/python

import argparse
import sys
from datetime import datetime
import logging
import threading
import serial


class Tee(object):
    """
    want print() and logging() to go to the console and a file
    don't know how else to do it
    """
    def __init__(self, *files):
        self.files = files

    def write(self, o):
        for f in self.files:
            f.write(o)

    def flush(self):
        for f in self.files:
            f.flush()

splog_name = datetime.strftime(datetime.now(), "spdbg_%Y_%m_%d_%H%M%S.log")
splog = open(splog_name, "w")
stdout_O = sys.stdout
sys.stdout = Tee(sys.stdout, splog)
PROMPT = 'spdbg> '
global SPOPEN
SPOPEN = True

logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG,
                    format="%(asctime)s:%(levelname)s:%(message)s")


def prompt():
    sys.stdout.write(PROMPT)
    sys.stdout.flush()


def serial_read(sp):
    global SPOPEN
    while SPOPEN:
        rxd = sp.read(1)
        if rxd:
            sys.stdout.write(rxd)
            sys.stdout.flush()
            # if spcom.handle_serial_input( rxd ) > 0:
            #  prompt()
    print('serial_read: closed.')


def handle_console(cdata, sp):
    global SPOPEN
    # print("handle_console(%s,%d)" % (type(cdata), len(cdata)))
    # TBD: filter for special commands
    if len(cdata) == 0:
        print("Quitting...")
        SPOPEN = False
    sp.write(cdata)

def main(args):
    # name = '/dev/tty.usbserial-FTF86JDH'
    name = '/dev/tty.usbserial-' + args.port
    print('serial port is <%s>' % name)
    ser = serial.Serial(
        port=name,
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0,
        xonxoff=False,
        rtscts=False,
        dsrdtr=False,
        writeTimeout=2
    )

    if ser.isOpen():
        print("serial port is OPEN")
    else:
        print("ERROR, serial port is not open")

    spth = threading.Thread(target=serial_read, args=(ser,))
    spth.start()

    prompt()

    while SPOPEN:  # gvars.console_open#
        crxd = sys.stdin.readline()
        handle_console(crxd, ser)
        prompt()

    ser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=str, default=None,
                        help="Name of serial port "
                        "(/dev/tty-usbserial is assumed)")
    args = parser.parse_args()
    main(args)
