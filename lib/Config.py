# -*- coding: utf-8 -*-

import os, re
import dns.resolver

class Config:
	# Number of ICMP packets per measurment
	echo_count = 10
	
	# Milliseconds
	ping_timeout = 3000
	
	# <min avg ms> <min lost %> <css color>
	colors = [
		{
			'minAvg': 0,
			'minLost': 0,
			'color': '#00FF01'
		},
		{
			'minAvg': -1,
			'minLost': -1,
			'color': '#000000'
		}
	]
	
	# First symbols
	display_desc = 12
	
	# Last octets
	display_ip = 2

	hosts = []
	
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
			if param == 'echo_count':
				self.echo_count = int(value)
			elif param == 'ping_timeout':
				self.ping_timeout = int(value)
			elif param == 'display_desc':
				self.display_desc = int(value)
			elif param == 'display_ip':
				self.display_ip = min(4, int(value))
			elif param == 'color':
				m = re.search('^((\d+) +(\d+)|none) +(#[0-9a-fA-F]+)$', value)
				if m:
					if m.group(1) == 'none':
						color = {'minAvg': -1, 'minLost': -1, 'color': m.group(4)}
					else:
						color = {'minAvg': int(m.group(2)), 'minLost': int(m.group(3)), 'color': m.group(4)}
					
					if (color['minAvg'] == -1) or (color['minLost'] == -1):
						color['minAvg'] = color['minLost'] = -1
					
					i = 0
					found = False
					while (i < len(self.colors)) and not found:
						stored = self.colors[i]
						if (color['minAvg'] == stored['minAvg']) and (color['minLost'] == stored['minLost']):
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
					try:
						for ip in dns.resolver.query(host, 'A'):
							pass
						self.hosts.append({'ip': str(ip), 'desc': desc})
					except:
						pass
