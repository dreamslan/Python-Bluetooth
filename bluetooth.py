#!/usr/bin/python
# -*- coding: utf-8 -*-

import types
import gobject
import subprocess
import dbus
from dbus.mainloop.glib import DBusGMainLoop
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)



##
#	Class which will manage all the errors that this API will send
#	@date 23/11/2012
#	@version 1.0
#	@author ManuelDeveloper (manueldeveloper@gmail.com)
class BluetoothException(Exception):
	
	##
	#	Builder of the class whose objective is save the error message
	#	@param information Relative information about the error
	#	@date 11/10/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)
	def __init__(self, information):
		self.information= information
	
	
	##
	#	Overload of the 'str' method which indicates the information to show when a class object is used by stdout
	#	@date 23/11/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)	
	def __str__(self):
		return repr(self.information)








##
#	API responsible of the bluetooth adapter management into UNIX systems based on BlueZ
#	@date		23/11/2012
#	@version	1.0
#	@author 	ManuelDeveloper (manueldeveloper@gmail.com)
class Bluetooth():
	
	""" Class attributes """
	
	# BlueZ system bus attributes
	_systemBus= None
	_manager= None
	
	
	
	
	""" Class Builder """
	##
	#	Builder of the class whose objective is check if the system has a bluetooth adapter and then, gets the reference to it
	#
	#	@retval		Bluetooth Object class which lets interact with the bluetooth adapter
	#	@exception	BluetoothException
	#	@date 		23/11/2012
	#	@version 	1.0
	#	@author 	ManuelDeveloper (manueldeveloper@gmail.com)
	def __init__(self):
		
		# Get access to the system bus
		Bluetooth._systemBus= dbus.SystemBus()		
		
		# Get the reference to BlueZ in the system
		Bluetooth._manager= Bluetooth._systemBus.get_object('org.bluez', '/')
		interfaceManager= dbus.Interface(Bluetooth._manager, 'org.bluez.Manager')
		
		# Get the reference to the bluetooth adapter
		try:
			adapterReference= interfaceManager.DefaultAdapter()			
			self.adapter= dbus.Interface(Bluetooth._systemBus.get_object('org.bluez', adapterReference), 'org.bluez.Adapter')
			self.adapter.connect_to_signal('PropertyChanged', self.propertyListener)
			self.adapter.connect_to_signal('DeviceFound', self.deviceFound)
		except:
			raise BluetoothException("The system does not have an bluetooth connection")
			
		# Initialize the internal flags
		self.isDiscovering= False
			
			
			
			
	""" General purpose methods """
	##
	#	Method which checks if the bluetooth adapter is On or Off
	#	@retval True if the adapter is ON
	#	@retval False if the adapter if OFF
	#	@date 27/09/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)
	def getPower(self):
		
		# Return the bluetooth adapter status
		properties= self.adapter.GetProperties()
		if properties['Powered'] == 1:
			return True
		else:
			return False
			
	
	##
	#	Method which turns On/Off the bluetooth adapter
	#	@param power Indicates if we want to turn On(True) or Off(False) the bluetooth adapter
	#	@date 27/09/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)
	def setPower(self, power):
		
		# Check the action
		if power is True:
			if self.getPower() is False:
				self.adapter.SetProperty('Powered', power) # Turn On
				self.propertyLoop= gobject.MainLoop()
				self.propertyLoop.run()	
				
		elif power is False:
			if self.getPower() is True:
				self.adapter.SetProperty('Powered', power) # Turn Off
				self.propertyLoop= gobject.MainLoop()
				self.propertyLoop.run()
	
	
	##
	#	Method which checks if the bluetooth visibility is On or Off
	#	@retval True if the bluetooth visibility is ON
	#	@retval False if the bluetooth visibility if OFF
	#	@exception	BluetoothException
	#	@date 27/09/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)
	def getVisibility(self):
		
		# Check if the bluetooth adapter is ON
		if self.getPower() is True:
			
			# Return the bluetooth visibility status
			properties= self.adapter.GetProperties()
			if properties['Discoverable'] == 1:
				return True
			else:
				return False
				
		else:
			raise BluetoothException("The bluetooth adapter is turned off")
	
	
	##
	#	Method which turns On/Off the bluetooth visibility
	#	@param visible Indicates if we want to make the bluetooth adapter Visible(True) or Invisible(False)
	#	@exception	BluetoothException
	#	@date 27/09/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)
	def setVisibility(self, visible):
		
		try:
			if (self.getVisibility() is False) and (visible is True): # Set visible
				self.adapter.SetProperty('Discoverable', visible)
				self.propertyLoop= gobject.MainLoop()
				self.propertyLoop.run()
				
			elif (self.getVisibility() is True) and (visible is False): # Set invisible
				self.adapter.SetProperty('Discoverable', visible)
				self.propertyLoop= gobject.MainLoop()
				self.propertyLoop.run()
				
		except BluetoothException as ex:
			raise ex
				
	
	##
	#	Method which returns the ASCII name of the bluetooth adapter
	#	@retval String with the name of the bluetooth adapter
	#	@date 27/09/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)
	def getName(self):
		
		# Return the name
		properties= self.adapter.GetProperties()
		return properties['Name']
		
	
	##
	#	Method which sets the ASCII name of the bluetooth adapter
	#	@param name String with the name of the bluetooth adapter
	#	@exception BluetoothException
	#	@date 27/09/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)
	def setName(self, name):

		# Check if the name is right
		if type(name) is types.StringType:
			# Sets the new name
			self.adapter.SetProperty('Name', name)
		
		else:
			raise BluetoothException("The name has an incorrect type (must be a string)")
			
			
	##
	#	Method which will receive all the signals that inform of the value change of the bluetooth adapter properties 
	#	@param name Name of the property changed
	#	@param value New value of the property
	#	@date 27/09/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)			
	def propertyListener(self, name, value):
		
		# Stop the loop needed to update the value of the property
		if name != "Discovering":
			self.propertyLoop.quit()
		
	
	
	""" Search methods """
	##
	#	Method which starts up the search process ()
	#	@param timeOut Duration in seconds of the search process, by default, are 5s
	#	@retval List List object whose content are tuples with the information of all devices found (MAC, Name, Type, CoD)
	#	@retval None If the adapter has not found any device
	#	@exception BluetoothExecption
	#	@date 14/12/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)	
	def search(self, timeOut= 5):
		
		# Check if the timeOut is right
		if type(timeOut) is types.IntType:
		
			# Check if there is a search process right now
			if self.isDiscovering is False:
				
				# Set up the internal flags
				self.devices= []
				self.isDiscovering= True
				self.searchLoop= gobject.MainLoop()
				
				# Start up the search process
				self.adapter.StartDiscovery()
				gobject.timeout_add(timeOut * 1000, self.searchTimeOut)		
				self.searchLoop.run()
				
				# Return the the information
				if len(self.devices) is 0:
					return None
				else:
					return self.devices
			
			else:
				raise BluetoothException("Right now, there is a search process")
		else:
			raise BluetoothException("The timeOut has an incorrect type (must be an int)")
	
	
	##
	#	Method which will called when the timeout of search process is reached and stops the process
	#	@date 14/12/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)	
	def searchTimeOut(self):
		
		self.adapter.StopDiscovery()
		self.isDiscovering= False
		self.searchLoop.quit()
		return False
	
	
	##
	#	Method which will called when the bluetooth adapter find a new device and will save its information in a general list
	#	@param address Bluetooth MAC of the discovered device
	#	@param properties Dictionary with all the information about the discovered device
	#	@date 14/12/2012
	#	@version 1.0
	#	@author ManuelDeveloper (manueldeveloper@gmail.com)	
	def deviceFound(self, address, properties):
		
		# First, check if there is a search process running
		if self.isDiscovering is True:
			
			# Get the important information about the discovered device
			address= properties['Address']
			cod= properties['Class']
			
			if 'Name' in properties:
				name= properties['Name']
			else:
				name= None
				
			if 'Icon' in properties:
				icon= properties['Icon']
			else:
				icon= None
			
			# Add the information to the general list
			self.devices.append( (address, name, icon, cod) )
