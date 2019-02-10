#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import signal

class EventProcessor():
    def __init__(self):
        self.tasks = []

    def signal_handler(self, sig, frame):
        print 'Signal trapped. Stopping tasks'
        self.stop_tasks()
        self.join_tasks()

    def start_tasks(self):
        print 'Starting tasks'
        for task in self.tasks:
            task.start()

    def stop_tasks(self):
        for task in self.tasks:
            task.stop()

    def join_tasks(self):
        for task in self.tasks:
            task.join()

    def run(self):
        # Setup signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
        self.start_tasks()

        # Block until signalled
        signal.pause()

        # Clean up threads
        self.stop_tasks()
        self.join_tasks()
        print "Eventprocessor exited cleanly"


if __name__ == "__main__":
    from event_listener import EventListener

    processor = EventProcessor()
    processor.tasks.append( EventListener('manna,hou,bisnap','power') )
    processor.run()
