#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from kafka import KafkaProducer

class EventEmitter():
    def __init__(self, servers, topic):
        self.servers = servers
        self.topic = topic
        self.producer = KafkaProducer(bootstrap_servers=self.servers)

    def send(self, dat):
        print (dat)
        self.producer.send(self.topic, dat.encode())
