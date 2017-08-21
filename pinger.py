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
	
	import signal
	from lib.Event import Event
	from lib.Probe import Probe
	from lib.Server import Server
	from threading import Lock
	class Global:
		pings = 0
		pingLock = Lock()
		event = Event()
		probes = []
		cfg = cfg

		LOG_ERROR = 0
		LOG_WARNING = 1
		LOG_INFO = 2
		LOG_DEBUG = 3
		
		def log (self, msg, logLevel = LOG_ERROR):
			if logLevel == self.LOG_ERROR:
				self.stop()
			
			if logLevel > cfg.logLevel:
				return
			
			levelMsg = ['ERROR', 'WARNING', 'INFO', 'DEBUG']
			
			logLine = list(time.localtime())[:6]
			logLine.append(levelMsg[logLevel])
			logLine.append(msg)
			print '[%d-%02d-%02d %02d:%02d:%02d] %s: %s' % tuple(logLine)
		
		def stop (self):
			os.unlink(cfg.appDirFile(cfg.pidFile))
	
	glb = Global()
	
	def sigHandler (signum, frame):
		if signum == signal.SIGHUP:
			glb.log('SIGHUP received', glb.LOG_INFO)
			return
		
		if signum == signal.SIGTERM:
			glb.log('Killed with SIGTERM', glb.LOG_INFO)
			glb.stop()
	
	signal.signal(signal.SIGHUP, sigHandler);
	signal.signal(signal.SIGTERM, sigHandler);
	#signal.signal(signal.SIG, sigHandler);
	
	glb.log('+++ Starting…', glb.LOG_INFO);
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
				glb.log('Probes have been changed', glb.LOG_INFO)
				httpd.probesChanged()
				glb.event.clear()
			if log:
				log.flush()
		glb.log('--- Stopping…', glb.LOG_INFO)
	except Exception as e:
		glb.log(e)
	
	for probe in glb.probes:
		probe.stop()
	httpd.stop()
	
	for probe in glb.probes:
		probe.join()
	httpd.join()
	
	glb.log('*** Bye', glb.LOG_INFO)
