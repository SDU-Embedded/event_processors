#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import threading,curses,json,time,signal,sys,copy
from datetime import datetime
from kafka import KafkaConsumer, KafkaProducer

class StateMonitor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

        self.state = False
        self.probability = 0.0
        self.on_gain = 5.0
        self.off_gain = 1.0
        self.max = 100.0
        self.min = 0.0
        self.period = 0.01

    def run(self):
        while not self.stop_event.is_set():
            if self.state:
                self.probability = self.probability + self.on_gain
                if self.probability > self.max:
                    self.probability = self.max
            else:
                self.probability = self.probability - self.off_gain
                if self.probability < self.min:
                    self.probability = self.min
            time.sleep(self.period)

    def stop(self):
        self.stop_event.set()

    def setState(self, state):
        #print "Setting state to " + str(state)
        self.state = state

    def getProbability(self):
        return self.probability


class EventListener(threading.Thread):
    def __init__(self, servers,topic):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        
        self.servers = servers
        self.topic = topic

        self.setState = None

    def stop(self):
        self.stop_event.set()

    def run(self):
        consumer = KafkaConsumer(bootstrap_servers=self.servers,auto_offset_reset='latest',consumer_timeout_ms=1000)
        consumer.subscribe([self.topic])

        while not self.stop_event.is_set():
            for message in consumer:
                # Parse content of event
                event = json.loads(message.value)
                
                #print "Received event " + str(event)
                if event['data']['event'] == 'onset':
                    self.setState(True)
                if event['data']['event'] == 'offset':
                    self.setState(False)

            
            if self.stop_event.is_set():
                break

        consumer.close()

class EventParser():
    def __init__(self,servers,topic):
        self.event = dict()
        self.contents = dict()
        self.contents["bird"] = 1
        self.contents["type"] = "bout"
        self.contents["duration"] = 0.0
        self.event["data"] = self.contents
        self.event["@timestamp"] = datetime.utcnow()
        self.last_onset_event = copy.deepcopy(self.event)
        self.event_emitter = EventEmitter(servers,topic)

    def get_time_since_last_event(self):
        current_time = datetime.utcnow()
        previous_time = self.event["@timestamp"]
        return (current_time - previous_time).total_seconds()

    def emit_event(self):
        tmp = copy.deepcopy(self.event)
        tmp["@timestamp"] = self.event["@timestamp"].isoformat()
        self.event_emitter.send( json.dumps(tmp) )

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

class EventEmitter():
    def __init__(self, servers, topic):
        self.servers = servers
        self.topic = topic
        self.producer = KafkaProducer(bootstrap_servers=self.servers)

    def send(self, dat):
        print (dat)
        self.producer.send(self.topic, dat.encode())

class Thresholder(threading.Thread):
    def __init__(self, servers, topic):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

        self.state = False

        self.getters = None

        self.upwards_threshold = 15.0
        self.downwards_threshold = 5.0
        self.period = 0.01
        
        self.event_parser = EventParser(servers, topic)

    def run(self):
        while not self.stop_event.is_set():
            probability = 0.0
            for getter in self.getters:
                probability = probability + getter()
            
            print str(probability)
            if self.state:
                if probability < self.downwards_threshold:
                    self.state = False
                    self.emitOff()
            else:
                if probability > self.upwards_threshold:
                    self.state = True
                    self.emitOn()
            time.sleep(self.period)
    
    def stop(self):
        self.stop_event.set()

    def emitOn(self):
        self.event_parser.evaluate('onset')
        #print 'Syllable onset'

    def emitOff(self):
        self.event_parser.evaluate('offset')
        #print 'Syllable offset'
            
            
class EventProcessor():
    def __init__(self, servers):
        self.servers = servers

        self.power_monitor = StateMonitor()
        self.power_listener = EventListener(self.servers, 'power')
        self.power_listener.setState = self.power_monitor.setState
        self.entropy_monitor = StateMonitor()
        self.entropy_listener = EventListener(self.servers, 'entropy')
        self.entropy_listener.setState = self.entropy_monitor.setState
        self.thresholder = Thresholder(self.servers, 'bout')
        self.thresholder.getters = [self.power_monitor.getProbability, self.entropy_monitor.getProbability]
    
        self.tasks = [self.power_monitor, self.power_listener, self.entropy_monitor, self.entropy_listener, self.thresholder]
        #self.tasks = [self.power_monitor, self.power_listener, self.thresholder]

    def signal_handler(self, sig, frame):
        print 'Signal trapped. Stopping tasks'
        self.stop_tasks()
        self.join_tasks()

    def start_tasks(self):
        for task in self.tasks:
            task.start()

    def stop_tasks(self):
        for task in self.tasks:
            task.stop()

    def join_tasks(self):
        for task in self.tasks:
            task.join()


if __name__ == "__main__":
    servers = 'manna,hou,bisnap'

    event_processor = EventProcessor(servers)

    signal.signal(signal.SIGINT, event_processor.signal_handler)
    event_processor.start_tasks()

    signal.pause()
