#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy,json
from datetime import datetime
from event_emitters import EventEmitter

class EventBuilder():
    def __init__(self, **data_arguments):
        self.contents = data_arguments
        self.contents["duration"] = 0.0

        self.event = dict()
        self.event["data"] = self.contents
        self.event["@timestamp"] = datetime.utcnow()

        self.last_onset_event = copy.deepcopy(self.event)
        
        self.send = None

    def get_time_since_last_event(self):
        current_time = datetime.utcnow()
        previous_time = self.event["@timestamp"]
        return (current_time - previous_time).total_seconds()

    def emit_event(self):
        tmp = copy.deepcopy(self.event)
        tmp["@timestamp"] = self.event["@timestamp"].isoformat()
        self.send( json.dumps(tmp) )

    def evaluate(self, dat):
        if 'onset' in dat:
            self.event["@timestamp"] = datetime.utcnow()
            self.event["data"]["event"] = dat
            self.event["data"]["duration"] = 0.0
            self.last_onset_event = copy.deepcopy(self.event)
            self.emit_event()
        else:
            duration = self.get_time_since_last_event()
            self.event = copy.deepcopy(self.last_onset_event)
            self.event["data"]["event"] = dat
            self.event["data"]["duration"] = duration
            self.emit_event()
