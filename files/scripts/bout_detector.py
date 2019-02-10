#!/usr/bin/env python
# -*- coding: utf-8 -*-

from event_processors import EventProcessor
from event_listeners import OnOffEventListener
from state_monitors import TwoLevelStateMonitor
from metric_processors import ProbabilityProcessor
from thresholders import Thresholder
from event_builders import EventBuilder
from event_emitters import EventEmitter

if __name__ == "__main__":

    
    # Setup event listeners
    power_event_listener = OnOffEventListener( servers='manna,hou,bisnap', topic='power' )
    entropy_event_listener = OnOffEventListener( servers='manna,hou,bisnap', topic='entropy' )
    
    # Setup state monitors
    power_state_monitor = TwoLevelStateMonitor( period=0.01, upwards_gain=0.03, downwards_gain=0.005 )
    entropy_state_monitor = TwoLevelStateMonitor( period=0.01, upwards_gain=0.03, downwards_gain=0.005 )
    
    power_event_listener.stateTransitionCallback = power_state_monitor.setState
    entropy_event_listener.stateTransitionCallback = entropy_state_monitor.setState

    # Setup metric processor
    metric_processor = ProbabilityProcessor( period=0.01 )
    
    metric_processor.getters.append( power_state_monitor.getProbability )
    metric_processor.getters.append( entropy_state_monitor.getProbability )
    
    # Setup thresholders
    thresholder = Thresholder( upwards_threshold=0.85, downwards_threshold=0.50 )
    metric_processor.setters.append( thresholder.evaluate )
    
    # Setup event builders
    builder = EventBuilder( bird="1", type="bout" )
    thresholder.emitEvent = builder.evaluate

    # Setup event emitters
    emitter = EventEmitter( servers='manna,hou,bisnap', topic='bout')
    builder.send = emitter.send
    
    # Setup and run event processor
    event_processor = EventProcessor()
    event_processor.tasks.append(power_event_listener)
    event_processor.tasks.append(entropy_event_listener)
    event_processor.tasks.append(power_state_monitor)
    event_processor.tasks.append(entropy_state_monitor)
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



