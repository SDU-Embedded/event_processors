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
    bout_event_listener = OnsetEventListener( servers='manna,hou,bisnap', topic='ats_bout' )

    # Setup state monitors
    bout_state_monitor = TimingStateMonitor()
    
    bout_event_listener.stateTransitionCallback = bout_state_monitor.setState
    
    # Setup and run event processor
    event_processor = EventProcessor()
    event_processor.tasks.append(bout_event_listener)
    event_processor.tasks.append(bout_state_monitor)
    event_processor.run()

