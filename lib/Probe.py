# -*- coding: utf-8 -*-

import os, re, time, errno
from threading import Thread
from subprocess import Popen, PIPE

class Probe (Thread):
	
	__running = True
	__changed = False
	color = None
	
	def __init__ (self, idx, host, cfg, glb):
		Thread.__init__(self)
		
		self.__idx = idx
		self.__host = host['host']
		self.__ip = host['ip']
		self.__cfg = cfg
		self.__glb = glb
		self.desc = host['desc'][0:cfg.displayDesc]
		
		if self.__ip:
			self.__setIp()
	
	def run (self):
		try:
			if self.__ip == '0.0.0.0':
				self.__dead()
			
			while self.__running:
				self.__changed = False
				if self.__ip:
					ping = self.__cfg.ping(self.__ip)
				else:
					ping = self.__cfg.ping(self.__host)
				
				self.__glb.pingLock.acquire()
				if self.__glb.pings < self.__cfg.simultaneousPings:
					self.__glb.pings += 1
					self.__glb.pingLock.release()
				else:
					self.__glb.pingLock.release()
					time.sleep(1)
					continue
				
				try:
					proc = Popen(ping, stdout = PIPE, stderr = PIPE)
				except OSError as e:
					self.__glb.pings -= 1
					if e.errno != errno.ENOMEM:
						raise e
					if self.__cfg.simultaneousPings > 1:
						self.__cfg.simultaneousPings -= 1
					continue
				
				(out, err) = proc.communicate()
				self.__glb.pings -= 1
				
				found = False
				for s in out.split('\n'):
					m = False
					if not self.__ip:
						# PING ya.ru (87.250.250.242)
						# PING 1.2.3.4 (1.2.3.4)
						# :empty output on non existent hostname:
						m = re.search('^PING %s \\((\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3})\\)' % self.__host, s)
						if m:
							self.__setIp(m.group(1))
						else:
							self.__setIp('0.0.0.0')
							self.__dead()
					
					if not m:
						m = re.search('(\d+)% packet loss', s)
						if m:
							self.__loss = int(m.group(1))
							found = True
						else:
							m = re.search('(?:rtt|round-trip) min/avg/max(?:/mdev|) = ([0-9.]+)/([0-9.]+)/([0-9.]+)(?:/([0-9.]+)|) ms', s)
							if m:
								self.__avg = float(m.group(2))
							else:
								self.__avg = -2
				
				colorDef = None
				if found:
					
					for c in self.__cfg.colors:
						if ((self.__loss >= c['minLoss']) or (self.__avg >= c['minAvg'])) and (not colorDef or (c['minLoss'] >= colorDef['minLoss'] ) or (c['minAvg'] >= colorDef['minAvg'])):
							colorDef = c
					
					if self.color != colorDef['color']:
						self.__changed = True
						self.color = colorDef['color']
				
				if self.__changed:
					self.__onChange()
				
				interval = self.__cfg.pingInterval
				while self.__running and (interval > 0):
					time.sleep(1)
					interval -= 1
		except Exception as e:
			self.__glb.log(e)
	
	def __onChange (self):
		self.__changed = False
		self.__glb.event.set(self.__idx)
	
	def __setIp (self, ip = None):
		if ip:
			self.__ip = ip
			self.__changed = True
		self.desc = '%s\n%s' % (self.desc, '.'.join(self.__ip.split('.')[4 - self.__cfg.displayIp:]))
	
	def __dead (self):
		self.__running = False
		for c in self.__cfg.colors:
			if c['minLoss'] == -1:
				self.color = c['color']
				self.__onChange()
				break
	
	def stop (self):
		self.__running = False
