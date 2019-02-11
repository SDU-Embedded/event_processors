#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import threading, time
from thresholders import Thresholder

class ProbabilityProcessor(threading.Thread):
    def __init__(self, period=0.01, debug=False):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

        self.period = period
        self.debug = debug

        self.setters = []
        self.getters = []

    def stop(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.is_set():
            prob = self.evaluate()
            
            if self.debug:
                print "Combined probability: " + str(prob)

            for setter in self.setters:
                setter(prob)

            time.sleep(self.period)

    def evaluate(self):
        probability = 0.0
        for getter in self.getters:
            probability = probability + getter()
        probability = probability / len(self.getters)
        return probability

