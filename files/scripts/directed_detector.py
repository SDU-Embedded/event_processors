#!/usr/bin/env python
# -*- coding: utf-8 -*-

from event_processors import EventProcessor
from event_listeners import PerchEventListener
from state_monitors import LinearStateMonitor
from metric_processors import ProbabilityProcessor
from thresholders import Thresholder
from event_builders import EventBuilder
from event_emitters import EventEmitter

if __name__ == "__main__":

    # Setup event listeners
    perch_event_listener = PerchEventListener('manna,hou,bisnap','ats_perch',bird=1 )
    bout_event_listener = OnOffEventListener('manna,hou,bisnap','ats_bout' )
 
    # Setup state monitors
    perch_state_monitor = LinearStateMonitor( period=0.1, upwards_gain=0.1, downwards_gain=0.1 )
    bout_state_monitor = LinearStateMonitor( period=0.1, upwards_gain=0.1, downwards_gain=0.1 )
    perch_event_listener.stateTransitionCallback = perch_state_monitor.setState
    bout_event_listener.stateTransitionCallback = bout_state_monitor.setState

    # Setup metric processor
    metric_processor = ProbabilityProcessor( period=0.1 )
    metric_processor.getters.append( perch_state_monitor.getProbability )
    metric_processor.getters.append( bout_state_monitor.getProbability )
    
    # Setup thresholders
    thresholder = Thresholder( upwards_threshold=0.8, downwards_threshold=0.55 )
    metric_processor.setters.append( thresholder.evaluate )
    
    # Setup event builders
    builder = EventBuilder( bird="1", type="directed" )
    thresholder.emitEvent = builder.evaluate

    # Setup event emitters
    emitter = EventEmitter( 'manna,hou,bisnap','ats_directed')
    builder.send = emitter.send
    
    # Setup and run event processor
    event_processor = EventProcessor()
    event_processor.tasks.append(perch_event_listener)
    event_processor.tasks.append(bout_event_listener)
    event_processor.tasks.append(perch_state_monitor)
    event_processor.tasks.append(bout_state_monitor)
    event_processor.tasks.append(metric_processor) 
    event_processor.run()

    
    
    #event_processor.tasks.append( TwoLevelStateMonitor(period=0.01, upwards_gain=0.03, downwards_gain=0.005) )
    #event_processor.tasks.append( OnOffEventListener(servers, 'power', event_processor.tasks[-1].setState) ) 
    #event_processor.tasks.append( TwoLevelStateMonitor(period=0.01, upwards_gain=0.03, downwards_gain=0.005) )
    #event_processor.tasks.append( OnOffEventListener(servers, 'entropy', event_processor.tasks[-1].setState) ) 
    #event_processor.tasks.append( ProbabilityProcessor( servers=servers, topic='bout', upwards_threshold=0.85, downwards_threshold=0.5, period=0.01, bird="1", type="bout" ) )
    #event_processor.tasks[-1].getters.append( event_processor.tasks[0].getProbability )
    #event_processor.tasks[-1].getters.append( event_processor.tasks[2].getProbability )
    #event_processor.run()



