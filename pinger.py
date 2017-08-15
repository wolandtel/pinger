#!/usr/bin/env python
# -*- coding: utf-8 -*-

if __name__ == '__main__':
	from lib.Config import Config
	cfg = Config()
	
	from lib.Event import Event
	from lib.Probe import Probe
	from threading import Lock
	class Global:
		pings = 0
		pingLock = Lock()
	
	glb = Global()
	event = Event()
	probes = []
	for host in cfg.hosts:
		probe = Probe(len(probes), host, cfg, glb, event)
		probes.append(probe)
		probe.start()
	
	while cfg.appDirFile(cfg.pidFile):
		event.wait(cfg.eventTimeout)
		if (event.isSet()):
			for p in event.probeIdxs:
				probe = probes[p]
				print probe.desc
				print probe.color
			event.clear()
	
	for probe in probes:
		probe.stop()
	
	for probe in probes:
		probe.join()
