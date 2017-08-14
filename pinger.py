#!/usr/bin/env python
# -*- coding: utf-8 -*-

if __name__ == '__main__':
	from lib.Config import Config
	cfg = Config()
	
	import os
	from lib.Event import Event
	from lib.Probe import Probe
	event = Event()
	probes = []
	for host in cfg.hosts:
		probe = Probe(len(probes), host, cfg, event)
		probes.append(probe)
		probe.start()
	
	for probe in probes:
		probe.stop()
	

	while os.path.exists('r'):
		event.wait(cfg.eventTimeout)
		if (event.isSet()):
			for p in event.probeIdxs:
				probe = probes[p]
				print probe.desc
				print probe.color
			event.clear()
	
	for probe in probes:
		probe.join()
