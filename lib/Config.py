# -*- coding: utf-8 -*-

import os, sys, re
from subprocess import Popen, PIPE

class Config:
	# LOG_ERROR, LOG_WARNING, LOG_INFO, LOG_DEBUG
	logLevel = 0
	
	httpBind = ''
	httpPort = 8080
	
	gridMaxWidth = 10
	
	# Number of ICMP packets per measurment
	echoCount = 10
	
	# Milliseconds
	echoTimeout = 3000
	
	# Seconds
	pingInterval = 60
	
	# <min avg ms> <min loss %> <css color>
	colors = [
		{
			'minAvg': 0,
			'minLoss': 0,
			'color': '#00FF01'
		},
		{
			'minAvg': -1,
			'minLoss': -1,
			'color': '#000000'
		}
	]
	
	# First symbols
	displayDesc = 12
	
	# Last octets
	displayIp = 2
	
	hosts = []
	
	eventTimeout = 1
	
	pidFile = 'pid'
	logFile = 'pinger.log'
	appDir = os.path.dirname(sys.argv[0])
	
	def __init__ (self, cfgPath = 'pinger.conf'):
		
		cfgPath = self.appDirFile(cfgPath)
		if not cfgPath:
			raise Exception('Configuration file not found')
		
		c = open(cfgPath, 'r')
		s = True
		while s:
			s = c.readline()
			if not s:
				continue
			
			m = re.search('^ *([_a-zA-Z0-9]+) *= *([^ ]|[^ ].*[^ ]) *\n$', s)
			if not m:
				continue
			
			param = m.group(1)
			value = m.group(2)
			if param == 'logLevel':
				self.logLevel = int(value)
			elif param == 'httpBind':
				self.httpBind = value
			elif param == 'httpPort':
				self.httpPort = int(value)
			elif param == 'gridMaxWidth':
				self.gridMaxWidth = int(value)
			elif param == 'echoCount':
				self.echoCount = int(value)
			elif param == 'echoTimeout':
				self.echoTimeout = int(value)
			elif param == 'pingInterval':
				self.pingInterval = int(value)
			elif param == 'displayDesc':
				self.displayDesc = int(value)
			elif param == 'displayIp':
				self.displayIp = min(4, int(value))
			elif param == 'color':
				m = re.search('^((\d+) +(\d+)|none) +(#[0-9a-fA-F]+)$', value)
				if m:
					if m.group(1) == 'none':
						color = {'minAvg': -1, 'minLoss': -1, 'color': m.group(4)}
					else:
						color = {'minAvg': int(m.group(2)), 'minLoss': int(m.group(3)), 'color': m.group(4)}
					
					if (color['minAvg'] == -1) or (color['minLoss'] == -1):
						color['minAvg'] = color['minLoss'] = -1
					
					i = 0
					found = False
					while (i < len(self.colors)) and not found:
						stored = self.colors[i]
						if (color['minAvg'] == stored['minAvg']) and (color['minLoss'] == stored['minLoss']):
							stored['color'] = color['color']
							found = True
						else:
							i += 1
					if not found:
						self.colors.append(color)
			elif param == 'host':
				m = re.search('([^ ]+) (.*)$', value)
				if m:
					host = m.group(1)
					desc = m.group(2)
					
					ip = False
					m = re.search('^(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})$', host)
					if m:
						ip = True
						for i in range(1, 5):
							try:
								if int(m.group(i)) > 255:
									ip = False
							except:
								ip = False
							
							if not ip:
								break;
					
					if ip:
						ip = host
					else:
						ip = None
					
					self.hosts.append({'host': host, 'ip': ip, 'desc': unicode(desc, 'utf8')})
		
		c.close()
		
		self.simultaneousPings = len(self.hosts)
	
	def ping (self, host = None, oneTime = False):
		if oneTime:
			count = 1
			timeout = 1
		else:
			count = self.echoCount
			timeout = self.echoTimeout
		
		ping = ['/bin/ping', '-qc%d' % count, '-W%d' % timeout]
		if host:
			ping.append(host)
		
		return ping
	
	def appDirFile (self, fileName, absent = False):
		if fileName[0] == '/':
			path = fileName
		else:
			path = os.path.join(self.appDir, fileName)
		
		if absent or os.path.exists(path):
			return path
		
		return None
