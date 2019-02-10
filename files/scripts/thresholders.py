#!/usr/bin/env python
# -*- coding: utf-8 -*-

from event_parsers import EventParser

class Thresholder():
    def __init__(self, upwards_threshold=0.0, downwards_threshold=0.0):
        self.state = False
        
        self.emitEvent = None

        self.upwards_threshold = upwards_threshold
        self.downwards_threshold = downwards_threshold

    def evaluate(self, probability):
        if self.state:
            if probability < self.downwards_threshold:
                self.state = False
                self.emitEvent('offset')
        else:
            if probability > self.upwards_threshold:
                self.state = True
                self.emitEvent('onset')

