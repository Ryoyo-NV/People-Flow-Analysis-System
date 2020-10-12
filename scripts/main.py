#!/usr/bin/env python3

#pylint: disable=wrong-import-position
import sys
sys.path.insert(0, '/*')

import tracker as tr
import config as conf
import message_manager as mm

if __name__ == '__main__':

	# Set user config class instance
	config = conf.Config()
	# Set message manager class instance
	message_manager = mm.MessageManager(config)

	# set tracker class instance
	tracker = tr.Tracker(message_manager)
	# start tracker
	sys.exit(tracker.start_tracker(sys.argv))
