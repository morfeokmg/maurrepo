'''
Copyright (c) <2012> Tarek Galal <tare2.galal@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this 
software and associated documentation files (the "Software"), to deal in the Software 
without restriction, including without limitation the rights to use, copy, modify, 
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to 
permit persons to whom the Software is furnished to do so, subject to the following 
conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR 
A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Updated By Mauricio Martinez <morfeokmg@gmail.com>
'''

import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
import time, datetime, sys
import re

if sys.version_info >= (3, 0):
	raw_input = input

from Yowsup.connectionmanager import YowsupConnectionManager

class WhatsappListenerClient:
	
	def __init__(self, keepAlive = True, sendReceipts = False):
		self.sendReceipts = sendReceipts
		
		connectionManager = YowsupConnectionManager()
		#connectionManager.setAutoPong(keepAlive)
		connectionManager.setAutoPong(True)

		self.signalsInterface = connectionManager.getSignalsInterface()
		self.methodsInterface = connectionManager.getMethodsInterface()
		
		self.signalsInterface.registerListener("message_received", self.onMessageReceived)
		self.signalsInterface.registerListener("group_messageReceived", self.group_messageReceived)
		self.signalsInterface.registerListener("auth_success", self.onAuthSuccess)
		self.signalsInterface.registerListener("auth_fail", self.onAuthFailed)
		self.signalsInterface.registerListener("disconnected", self.onDisconnected)
		
		self.cm = connectionManager

	def listening(self):
		while True:
			raw_input()	

	def login(self, username, password):
		self.username = username
		self.methodsInterface.call("auth_login", (username, password))
		
		#while True:
			#raw_input()	

	def onAuthSuccess(self, username):
		print("Authed %s" % username)
		self.methodsInterface.call("ready")

	def onAuthFailed(self, username, err):
		print("Auth Failed!")

	def onDisconnected(self, reason):
		print("Disconnected because %s" %reason)

	def onMessageReceived(self, messageId, jid, messageContent, timestamp, wantsReceipt, pushName, isBroadCast):
		formattedDate = datetime.datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M:%S')
		print("%s [%s]:%s"%(jid, formattedDate, messageContent))

		#if wantsReceipt and self.sendReceipts:
		self.methodsInterface.call("message_ack", (jid, messageId))

	def group_messageReceived(self, messageId, jid, author, messageContent, timestamp, wantsReceipt, pushName):
		self.sentCache = {}
		self.groupsPerms = ['5215544031190-1416524784']
		self.usersPerms = ['5215549884199']
		######################################################################################################
		## Mensaje en modo depuracion para poder visualizar la informacion completa del mensaje 
		## e identificar los valores completos 
		######################################################################################################
		#finalMessage = "messageID: %s, jid: %s, author: %s, messageContent: %s, timestamp: %s, wantsReceipt: %s, pushName: %s" % (str(messageId), jid, author, messageContent, str(timestamp), wantsReceipt, pushName)

		finalMessage = messageContent
		group = str(jid.split('@')[0])
		userPriv = str(author.split('@')[0])
		#if (group == '5215544031190-1416524784'):
		if (group in self.groupsPerms):
			if (userPriv in self.usersPerms):				
				try:
					foundCommands = re.search(':::(.+?):::',messageContent).group(1)
				except AttributeError as AE: 
					foundCommands = None
	
				finalMessage='CommandsGroup>> '+str(foundCommands)
				if foundCommands:
					commandsMapping=['ejecuta','consulta','grocery']
					totalParameters=foundCommands.split(':')
					if (len(totalParameters)==2):
						tipoComando=totalParameters[0]
						comandoExec=totalParameters[1]
	
						if (tipoComando in commandsMapping):	
							if (tipoComando=='grocery' and comandoExec=="huevos"):
								message="Huevos a todos gays jejejejejeje"
							elif (tipoComando=='ejecuta' and comandoExec=='Desconecta'):
								self.methodsInterface.call("disconnected","Desconecion Manual Proceso")
								message="Se ha desconectado de la session de WATTTSSSS. Se ha finalizado el proceso"
							elif (tipoComando=='ejecuta'):
								#message=os.popen4(comandoExec).read() 
								stdInp,stdOutp=os.popen4(comandoExec)
								message=str(stdInp)+'::::'+str(stdOutp)
							else:
								message="Run Others"
						else:
							message="Fallo"

					msgId = self.methodsInterface.call("message_send", (jid, message))
					self.sentCache[msgId] = [int(time.time()), message]

				else:
					#jid = group
					totalParameters=[]
					message="El comando es incompleto o no tiene los parametros necesarios... Longitud Mensajes: "+str(len(totalParameters))
					msgId = self.methodsInterface.call("message_send", (jid, message))
					self.sentCache[msgId] = [int(time.time()), message]				


		
        	formattedDate = datetime.datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M:%S')
        	#print("%s [%s]:%s"%(jid, formattedDate, messageContent))
        	print("[Auth:%s] [JID: %s] [%s]:%s"%(author, jid,formattedDate, finalMessage))

        	#if wantsReceipt and self.sendReceipts:        	
         	self.methodsInterface.call("message_ack", (jid, messageId))





