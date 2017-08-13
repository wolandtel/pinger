# -*- coding: utf-8 -*-

from threading import Event

class Event:
	__e = Event()
	probeIdxs = []
	
	# FIX: add Lock
	def set (self, idx):
		self.probeIdxs.append(idx)
		self.__e.set()
	
	def isSet (self):
		return self.__e.isSet()
	
	# FIX: check Lock
	def clear (self):
		self.probeIdxs = []
		self.__e.clear()
	
	def wait (self, timeout = None):
		self.__e.wait(timeout)
