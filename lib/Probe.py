# -*- coding: utf-8 -*-

import os, re, time
from threading import Thread
from subprocess import Popen, PIPE

class Probe (Thread):
	
	__running = True
	__changed = False
	color = None
	
	def __init__ (self, idx, host, cfg, onChange):
		Thread.__init__(self)
		
		self.__idx = idx
		self.__ip = host['ip']
		self.__cfg = cfg
		self.__eventOnChange = onChange
		self.desc = '%s\n%s' % (host['desc'][0:cfg.displayDesc], '.'.join(self.__ip.split('.')[4 - cfg.displayIp:]))
	
	def run (self):
		if self.__ip == '0.0.0.0':
			self.__running = False
			for c in self.__cfg.colors:
				if c['minLoss'] == -1:
					self.color = c['color']
					self.__onChange()
		
		while self.__running:
			self.__changed = False
			ping = self.__cfg.ping(self.__ip)
			proc = Popen(ping, stdout = PIPE, stderr = PIPE)
			(out, err) = proc.communicate()
			found = 0
			for s in out.split('\n'):
				m = re.search('(\d+)% packet loss', s)
				if m:
					self.__loss = int(m.group(1))
					found |= 1
				else:
					m = re.search('rtt min/avg/max/mdev = ([0-9.]+)/([0-9.]+)/([0-9.]+)/([0-9.]+) ms', s)
					if m:
						found |= 2
						self.__avg = float(m.group(2))
			
			colorDef = None
			if found == 3:
				
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
	
	def __onChange (self):
		self.__eventOnChange.set(self.__idx)
	
	def stop (self):
		self.__running = False
