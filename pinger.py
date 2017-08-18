#!/usr/bin/env python
# -*- coding: utf-8 -*-

if __name__ == '__main__':
	import os, time, sys
	from lib.Config import Config
	cfg = Config()
	
	pid = os.fork ()
	if pid == 0:
		time.sleep(0.1)
	else:
		p = open(cfg.appDirFile(cfg.pidFile, True), 'w')
		p.write(str(pid))
		p.close()
		sys.exit(0)
	
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
	
	try:
		while cfg.appDirFile(cfg.pidFile):
			glb.event.wait(0.1)
			if (glb.event.isSet()):
				httpd.probesChanged()
				glb.event.clear()
	except:
		pass
	
	for probe in glb.probes:
		probe.stop()
	httpd.stop()
	
	for probe in glb.probes:
		probe.join()
	httpd.join()
