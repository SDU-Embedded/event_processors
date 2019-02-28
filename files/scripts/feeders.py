#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import threading, time

class FileFeeder(threading.Thread):
    def __init__(self, filename, period=0.01, debug=False):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

        self.filename = filename
        self.period = period
        self.debug = debug

        self.setters = []

    def stop(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.is_set():
            try:
                with open(self.filename) as file_handle:
                    for line in file_handle.readlines():
                        try:
                            value = float(line)
                        except:
                            value = 0.0
            
                        if self.debug:
                            print "Value: " + str(value)

                        for setter in self.setters:
                            setter(value)

                        time.sleep(self.period)
            except:
                pass
            self.stop()

if __name__ == "__main__":
    feeder = FileFeeder('testfile.txt', period=0.5)

    def dummySetter(value):
        print value
    
    feeder.setters.append(dummySetter)
    feeder.start()

