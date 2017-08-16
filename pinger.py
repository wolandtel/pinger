#!/usr/bin/env python
# -*- coding: utf-8 -*-

if __name__ == '__main__':
	from lib.Config import Config
	cfg = Config()
	
	from lib.Event import Event
	from lib.Probe import Probe
	from lib.Server import Server
	from threading import Lock
	class Global:
		pings = 0
		pingLock = Lock()
		event = Event()
		probes = []
	glb = Global()
	
	httpd = Server(cfg, glb)
	httpd.start()
	
	for host in cfg.hosts:
		probe = Probe(len(glb.probes), host, cfg, glb)
		glb.probes.append(probe)
		probe.start()
	
	while cfg.appDirFile(cfg.pidFile):
		glb.event.wait(cfg.eventTimeout)
		if (glb.event.isSet()):
			httpd.probesChanged()
			glb.event.clear()
	
	for probe in glb.probes:
		probe.stop()
	httpd.stop()
	
	for probe in glb.probes:
		probe.join()
	httpd.join()
