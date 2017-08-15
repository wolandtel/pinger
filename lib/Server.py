# -*- coding: utf-8 -*-

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
		<link rel="stylesheet" href="styles.css" />
		<script src="main.js"></script>
	</head>
	<body>
	</body>
</html>''')
	
	def __rCss (self):
		self.__send_headers('text/css')
		self.wfile.write('''
''')

	def __rJs (self):
		self.__send_headers('text/javascript')
		self.wfile.write('''
''')

class Server (Thread):
	__listen = ''
	__protocol = "HTTP/1.1"
	
	def __init__ (self, port = 8080):
		Thread.__init__(self)
		
		self.__httpd = HTTPServer((self.__listen, port), HTTPRequestHandler)
	
	def run (self):
		self.__httpd.serve_forever()
	
	def stop (self):
		self.__httpd.shutdown()
