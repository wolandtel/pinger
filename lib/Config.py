# -*- coding: utf-8 -*-

import os, re
from subprocess import Popen, PIPE

class Config:
	# Number of ICMP packets per measurment
	echoCount = 10
	
	# Milliseconds
	echoTimeout = 3000
	
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
	
	def __init__ (self, path = 'pinger.conf'):
		
		if not os.path.exists(path):
			raise Exception('Configuration file not found')
		
		c = open(path, 'r')
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
			if param == 'echoCount':
				self.echoCount = int(value)
			elif param == 'echoTimeout':
				self.echoTimeout = int(value)
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
						# PING ya.ru (87.250.250.242)
						# PING 1.2.3.4 (1.2.3.4)
						# :empty output on non existent hostname:
						ping = self.ping(host)
						proc = Popen(ping, stdout = PIPE, stderr = PIPE)
						(out, err) = proc.communicate()
						
						m = re.search('^PING %s \\((\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3})\\)' % host, out)
						if m:
							ip = m.group(1)
						else:
							ip = '0.0.0.0'
					
					self.hosts.append({'ip': ip, 'desc': desc})
		
	def ping (self, host = None):
		ping = ['/bin/ping', '-qc%d' % self.echoCount, '-W%d' % self.echoTimeout]
		if host:
			ping.append(host)
		
		return ping
