# -*- coding: utf-8 -*-

import math
from threading import Thread
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

class HTTPRequestHandler (BaseHTTPRequestHandler):
	def do_GET (self):
		if self.path in ['/', '/index.html']:
			self.__rIndex()
		elif self.path == '/styles.css':
			self.__rCss()
		elif self.path == '/main.js':
			self.__rJs()
		else:
			self.__send_headers()
	
	def __send_headers (self, contentType = None):
		if contentType:
			self.send_response(200)
			self.send_header('Content-type', contentType)
			self.end_headers()
		
		else:
			self.send_response(404)
			self.end_headers()
		
	def __rIndex (self):
		self.__send_headers('text/html')
		self.wfile.write('''<!DOCTYPE html>
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
		<link rel="stylesheet" href="styles.css" />
		<script src="main.js"></script>
	</head>
	<body>
		<div id="page">
			%s
		</div>
	</body>
</html>''' % self.server.hosts())
	
	def __rCss (self):
		self.__send_headers('text/css')
		self.wfile.write('''
#page
{
	position: relative;
	height: 100%;
	width: 100vh
}

.host
{
	position: relative;
	float: left;
	border: 1px black solid;
}

.host .text {
	position: absolute;
	left: 0;
	top: 0;
	right: 0;
	bottom: 0;
	padding: 5%;
}
''')

	def __rJs (self):
		self.__send_headers('text/javascript')
		self.wfile.write('''
setInterval(function () { window.location.reload(); }, 10000)
''')

class CustomServer (HTTPServer):
	def __init__ (self, cfg, glb):
		HTTPServer.__init__(self, (cfg.httpBind, cfg.httpPort), HTTPRequestHandler)
		
		self.__cfg = cfg
		self.__glb = glb
	
	def hosts (self):
		width = 100 / min(math.ceil(math.sqrt(len(self.__glb.probes))), self.__cfg.gridMaxWidth)
		hosts = ''
		for probe in self.__glb.probes:
			if probe.color:
				bgColor = probe.color
			else:
				bgColor = '#FFF'
			
			if bgColor == '#000000':
				color = '#FFF'
			else:
				color = '#000'
			
			hosts += '<div class="host" style="width: calc(%f%% - 2px); padding-top: calc(%f%% - 2px); color: %s; background-color: %s"><div class="text">%s</div></div>' % \
				(width, width, color, bgColor, probe.desc.replace('\n', '<br />'))
		
		return hosts

class Server (Thread):
	__listen = ''
	__protocol = "HTTP/1.1"
	
	def __init__ (self, cfg, glb):
		Thread.__init__(self)
		
		self.__cfg = cfg
		self.__glb = glb
		self.__httpd = CustomServer(cfg, glb)
	
	def run (self):
		self.__httpd.serve_forever()
	
	def stop (self):
		self.__httpd.shutdown()
	
	def probesChanged (self):
		pass

