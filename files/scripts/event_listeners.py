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


if __name__ == "__main__":
    listener = EventListener('manna,hou,bisnap','power')

    signal.signal(signal.SIGINT, listener.stop) 
    listener.start()
    signal.pause()
    listener.join()

