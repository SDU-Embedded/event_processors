#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading,json,signal
from kafka import KafkaConsumer

class EventListener(threading.Thread):
    def __init__(self,servers,topic):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

        self.servers = servers
        self.topic = topic

        self.consumer = None
        self.event = None

    def stop(self, sig=None, frame=None):
        self.stop_event.set()

    def run(self):
        self.consumer = KafkaConsumer( bootstrap_servers=self.servers, auto_offset_reset='latest', consumer_timeout_ms=1000)
        self.consumer.subscribe( [self.topic] )

        while not self.stop_event.is_set():
            for message in self.consumer:
                # Parse content of event
                self.event = json.loads(message.value)
                self.evaluate_event()

            if self.stop_event.is_set():
                break
        self.consumer.close()

    def evaluate_event(self):
        print self.event

class OnOffEventListener(EventListener):
    def __init__(self, servers='', topic=''):
        EventListener.__init__(self, servers, topic)
        self.stateTransitionCallback = None

    def evaluate_event(self):
        if self.event['data']['event'] == 'onset':
            self.stateTransitionCallback(True)
        if self.event['data']['event'] == 'offset':
            self.stateTransitionCallback(False)


class PerchEventListener(EventListener):
    def __init__(self, servers='', topic='', bird=0, debug=False):
        EventListener.__init__(self, servers, topic)
        self.stateTransitionCallback = self.print_state
        self.bird = int(bird)
        self.debug = debug
        if self.debug:
            print "Initialised perch event detector for bird " + str(self.bird)

    def evaluate_event(self):
        if self.debug:
            print "Perch event listener for bird " + str(self.bird) + " received event"
        
        if self.event['data']['duration'] == 0.0: 
            if self.event['data']['position'] == 'FRONT' and self.event['data']['id'] == self.bird:
                if self.debug:
                    print "Bird " + str(self.bird) + " is perched"
                self.stateTransitionCallback(True)
            else:
                self.stateTransitionCallback(False)

    def print_state(self, state):
        print "Perch event listener for bird " + str(self.bird) + " attempted state change to " +str(state)

if __name__ == "__main__":
    listener1 = PerchEventListener('manna,hou,bisnap','perch_sensor',bird=1, debug=True )
    listener2 = PerchEventListener('manna,hou,bisnap','perch_sensor',bird=2, debug=True )

    def signalHandler(sig, frame):
        print "\nSignal " + str(sig) + " received."
        listener1.stop()
        listener2.stop()

    signal.signal(signal.SIGINT, signalHandler) 
    listener1.start()
    listener2.start()
    signal.pause()
    listener1.join()
    listener2.join()

