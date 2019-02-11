#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import threading,time

class StateMonitor(threading.Thread):
    def __init__(self, period=0.01, debug=False):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

        self.period = period
        self.debug = debug
        self.state = None
        self.probability = 0.0

        if self.debug:
            print "Initialised state monitor"

    def run(self):
        while not self.stop_event.is_set():
            self.evaluate()
            #if self.debug:
            #    print "Probability: " + str(self.probability)
            time.sleep(self.period)

    def evaluate(self):
        pass

    def stop(self):
        self.stop_event.set()

    def setState(self, state):
        if self.debug:
            print "Received state transition event " + str(state)
        self.state = state

    def getProbability(self):
        return self.probability


class LinearStateMonitor(StateMonitor):
    def __init__(self, period=0.01, upwards_gain=0.01, downwards_gain=0.01, debug=False):
        StateMonitor.__init__(self, period, debug)

        self.upwards_gain = upwards_gain
        self.downwards_gain = downwards_gain

        self.state = False
        self.probability_max = 1.0
        self.probability_min = 0.0

    def evaluate(self):
        if self.state:
            self.probability = self.probability + self.upwards_gain
            if self.probability > self.probability_max:
                self.probability = self.probability_max
        else:
            self.probability = self.probability - self.downwards_gain
            if self.probability < self.probability_min:
                self.probability = self.probability_min


class TwoLevelStateMonitor(StateMonitor):
    def __init__(self, period=0.01, upwards_gain=0.01, downwards_gain=0.01, debug=False):
        StateMonitor.__init__(self, period)

        self.low_factor = 1.0
        self.high_factor = 0.5

        self.low_upwards_gain = upwards_gain * self.low_factor
        self.low_downwards_gain = downwards_gain * self.low_factor

        self.high_upwards_gain = upwards_gain * self.high_factor
        self.high_downwards_gain = downwards_gain * self.high_factor

        self.state = False
        self.probability_max = 1.0
        self.probability_min = 0.0

        self.low_region = 0.60
        self.high_region = 0.80

    def evaluate(self):
        probability = self.probability
        if self.state:
            if probability < self.low_region or probability > self.high_region:
                probability = probability + self.low_upwards_gain
            else:
                probability = probability + self.high_upwards_gain
        else:
            if probability < self.low_region or probability > self.high_region:
                probability = probability - self.low_downwards_gain
            else:
                probability = probability - self.high_downwards_gain

        if probability > self.probability_max:
            probability = self.probability_max
        if probability < self.probability_min:
            probability = self.probability_min

        self.probability = probability

