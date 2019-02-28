#!/usr/bin/env python
# -*- coding: utf-8 -*-

from event_processors import EventProcessor
from feeders import FileFeeder
from thresholders import Thresholder
from event_builders import EventBuilder
from event_emitters import EventEmitter


if __name__ == "__main__":

    # Feed from file
    feeder = FileFeeder('/home/leon/unbiased.csv', period=0.003)

    # Setup thresholders
    thresholder = Thresholder( upwards_threshold=0.25, downwards_threshold=0.1 )
    feeder.setters.append( thresholder.evaluate )
    
    # Setup event builders
    builder = EventBuilder( type="bat" )
    thresholder.emitEvent = builder.evaluate

    # Setup event emitters
    emitter = EventEmitter( servers='manna,hou,bisnap', topic='bats')
    builder.send = emitter.send
    
    # Setup and run event processor
    event_processor = EventProcessor()
    event_processor.tasks.append(feeder)
    event_processor.run()
