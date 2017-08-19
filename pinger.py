#!/usr/bin/env python
# -*- coding: utf-8 -*-

if __name__ == '__main__':
	import os, time, sys
	from lib.Config import Config
	cfg = Config()
	
	pid = os.fork ()
	if pid:
		p = open(cfg.appDirFile(cfg.pidFile, True), 'w')
		p.write(str(pid))
		p.close()
		sys.exit(0)
	
	log = open(cfg.appDirFile(cfg.logFile, True), 'a')
	if log:
		sys.stdout = log
		sys.stderr = log
	time.sleep(0.1)
	
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
			if log:
				log.flush()
	except Exception as e:
		print e
	
	for probe in glb.probes:
		probe.stop()
	httpd.stop()
	
	for probe in glb.probes:
		probe.join()
	httpd.join()
