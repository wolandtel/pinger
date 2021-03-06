# -*- coding: utf-8 -*-

import math, time
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
		elif self.path == '/changed':
			self.__rChanged()
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
function CreateRequest()
{
	var Request = false;
	
	if (window.XMLHttpRequest)
	{
		//Gecko-совместимые браузеры, Safari, Konqueror
		Request = new XMLHttpRequest();
	}
	else if (window.ActiveXObject)
	{
		//Internet explorer
		try
		{
			Request = new ActiveXObject("Microsoft.XMLHTTP");
		}
		catch (CatchException)
		{
			Request = new ActiveXObject("Msxml2.XMLHTTP");
		}
	}
	
	return Request;
} 

/*
Функция посылки запроса к файлу на сервере
r_method  - тип запроса: GET или POST
r_path    - путь к файлу
r_args    - аргументы вида a=1&b=2&c=3...
r_handler - функция-обработчик ответа от сервера
*/
function SendRequest(r_method, r_path, r_args, r_handler)
{
	//Создаём запрос
	var Request = CreateRequest();
	
	//Проверяем существование запроса еще раз
	if (!Request)
		return;
	
	//Назначаем пользовательский обработчик
	Request.onreadystatechange = function()
	{
		//Если обмен данными завершен
		if (Request.readyState == 4)
		{
			//Передаем управление обработчику пользователя
			r_handler(Request);
		}
	}
	
	//Проверяем, если требуется сделать GET-запрос
	if (r_method.toLowerCase() == "get" && r_args.length > 0)
		r_path += "?" + r_args;
	
	//Инициализируем соединение1
	Request.open(r_method, r_path, true);
	
	if (r_method.toLowerCase() == "post")
	{
		//Если это POST-запрос
		
		//Устанавливаем заголовок
		Request.setRequestHeader("Content-Type","application/x-www-form-urlencoded; charset=utf-8");
		//Посылаем запрос
		Request.send(r_args);
	}
	else
	{
		//Посылаем нуль-запрос
		Request.send(null);
	}
}

online = true;
changed = %d;

setInterval(function () {
		SendRequest('GET', '/changed', '', function (Request) {
				if (Request.status == 200)
				{
					var needReload = false;
					if (!online)
					{
						online = true;
						document.getElementById('page').setAttribute('style', '');
						needReload = true;
					}
					
					if (Request.responseText > changed)
					{
						changed = Request.responseText;
						needReload = true;
					}
					
					if (needReload)
						location.href='';
				}
				else
				{
					document.getElementById('page').setAttribute('style', 'opacity: 0.3');
					online = false;
				}
			});
	}, 1000);
''' % self.server.lastChange)
	
	def __rChanged (self):
		self.__send_headers('text/plain')
		self.wfile.write(self.server.lastChange)

class CustomServer (HTTPServer):
	lastChange = int(time.time())
	
	def __init__ (self, cfg, glb):
		HTTPServer.allow_reuse_address = True
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
				(width, width, color, bgColor, probe.desc.replace('\n', '<br />').encode('utf8'))
		
		return hosts
	
	def probesChanged (self):
		self.lastChange = int(time.time())

class Server (Thread):
	__listen = ''
	__protocol = "HTTP/1.1"
	
	def __init__ (self, cfg, glb):
		Thread.__init__(self)
		
		self.__cfg = cfg
		self.__glb = glb
		self.__httpd = CustomServer(cfg, glb)
	
	def run (self):
		try:
			self.__httpd.serve_forever()
		except Exception as e:
			self.__glb.log(e)
	
	def stop (self):
		self.__httpd.shutdown()
	
	def probesChanged (self):
		self.__httpd.probesChanged()

