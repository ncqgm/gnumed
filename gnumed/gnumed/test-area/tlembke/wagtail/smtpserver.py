#!/usr/bin/python

import smtpd, asyncore, sys
from email import Parser
import smtplib
import urllib
import getpass
import string,re
try:
    import GnuPGInterface
except ImportError:
    print "You need to have GnuPGInterface installed. It is available from http://py-gnupg.sourceforge.net/"


class OurServer(smtpd.SMTPServer):
	
	#This is the callback from SMTPServer that all SMPTServers
	#must implement to handle messages
	def process_message(self, peer, mailfrom, rcpttos, data):
		ipaddr=peer[0]
		print "Message sent from %s" %ipaddr
		if ipaddr[0:3]==localNetwork:
			#Parse the message into an email.Message instance
			p = Parser.Parser()
			m = p.parsestr(data)
			print "Received Message"
			body=m.get_payload(decode=1)
			toAddr=m['To']
			if string.find(toAddr,'<')>0:
				toAddr=re.search("<(?P<email>.+)>",toAddr).group('email')
			status,encMessage=gnupg.encryptMessage(body,toAddr)
			if status==1:
				m.set_payload(encMessage)
				self.sendEncMessage(m)
				status=''
			else:
				print "Error in encrypting mesage"
		else:
			print "Not authorised smtp user"
			status="Not authorised smtp user"
		return status
		
		
	def sendEncMessage(self,msg):
		msgStr=msg.as_string()
		print "Connecting to SMTP server ......."
		try:
			server = smtplib.SMTP(smtpServer)
			server.set_debuglevel(1)
			server.sendmail( msg['From'], msg['To'], msgStr)
			server.quit() 
			print "Message sent"
			logText= "SEND Message sent encrypted to %s\n" % (msg['To'])
		except:
			logText="Error in sending message\n"
		wagLog('mail',logText)

class wtKeysClass(GnuPGInterface.GnuPG):
	"Class to provide interface between GnuPG and Python"
	def __init__(self):
		GnuPGInterface.GnuPG.__init__(self)
		self.setup_my_options()

	def setup_my_options(self):
		self.options.armor = 1
		self.options.meta_interactive = 0
		self.options.extra_args.append('--no-secmem-warning')
		
		
    	
	def lookupLocal(self,emailAddr):
		print "checking local lookup %s" %keyholdersFile
		try:
			file=open(keyholdersFile,"r")
			theString=file.read()
			file.close()
			theMatch="^"+emailAddr+",(?P<Timestamp>\w+),(?P<Name>[\w\s]+),(?P<Keypref>\w+),(?P<GPGKeyID>\w+),(?P<CAKeyID>\w+)"
			p=re.search(theMatch,theString,re.M)
			return p
		except:
			return "IOerror"
		
	def lookupRemote(self,emailAddr):
		print "checking remote lookup %s" %wtServer
		wtserverString=wtServer+emailAddr
		try:
			page=urllib.urlopen(wtserverString)
			theString=page.read()
			page.close
			theMatch="^"+emailAddr+",(?P<Timestamp>\w+),(?P<Name>[\w\s]+),(?P<Keypref>\w+),(?P<GPGKeyID>\w+),(?P<CAKeyID>\w+)"
			p=re.search(theMatch,theString,re.M)
			print "found %s" %theString
			return p
		except:
			print "Unable to access wagtail server %s" % wtserverString
			return "IOerror"
	
	def downloadGPG(self,keyID):
		gnupg = GnuPGInterface.GnuPG()
	
		# set options
		gnupg.options.armor = 1
		gnupg.options.meta_interactive = 0
		gnupg.options.extra_args.append('--no-secmem-warning')
	
		# create handles in p1
		
		p1=gnupg.run( ['--recv-keys'],args=[keyID],create_fhs=['stdout'])
	
		# read handles
		keylist = p1.handles['stdout'].read()
		p1.handles['stdout'].close()
	
		# process cleanup
		p1.wait()
		print keylist
		print "Key %s saved to local keyring" % keyID
	
	def downloadCA(self,keyID):
		pass
		
	def getKeyID(self,toAddr):
		# See if recipient is current in local Wagtail Lookup Table
		keyID=0
		pref=0
		returnText=''
		keyholder=self.lookupLocal(toAddr)
		if keyholder=="IOerror":
			returnText= "Local IOerror"
		elif keyholder==None:   # not found in local lookup
			keyholder=self.lookupRemote(toAddr)
			if keyholder=="IOerror":  #no access to remote lookup
				returnText="Remote IOerror"
			elif keyholder==None: # not found in remote lookup
				returnText="Not in Wagtail"
			else:                   # found remotely
				# append local keyholders information
				keyText=toAddr+","+keyholder.group('Timestamp')+","+keyholder.group('Name')+","+keyholder.group('Keypref')+","+keyholder.group('GPGKeyID')+","+keyholder.group('CAKeyID')+"\n"
				file=open(keyholdersFile,"a")
				file.write(keyText)
				file.close()
				# download GPG key to local keychain
				
				if keyholder.group('GPGKeyID')>0:
					self.downloadGPG(keyholder.group('GPGKeyID'))
				if keyholder.group('CAKeyID')>0:	
					self.downloadCA(keyholder.group('CAKeyID'))
				pref=1
				keyID=keyholder.group('GPGKeyID')
				if keyholder.group('Keypref')==2:
					keyID=keyholder.group('CAKeyID')
					pref=2
		
		else:   # found in local lookup
			pref=1
			keyID=keyholder.group('GPGKeyID')
			if keyholder.group('Keypref')==2:   # GPG preferred
				keyID=keyholder.group('CAKeyID')
				pref=2
		return keyID,pref,returnText
	
	
		
	def encryptMessage(self,message,toAddr):
		# get recepients preferred encryption and keyID
		keyID,prefEnc,errorMsg=self.getKeyID(toAddr)
		status=errorMsg
		returnText=''
		if keyID>0:     # key found
			if prefEnc==1:   # GPG preferred
				status,returnText=self.encryptGPG(message,keyID)
			else:                         # CA preferred
				status,returnText=self.encryptCA(message,keyID)
		return status,returnText
				
	def encryptCA(self,message,keyID):
		return "CA Unavailable"
		
	def encryptGPG(self,message,keyID):

		self.options.recipients = [keyID]
		#gnupg.options.always_trust=1
		encryptedYet=0
		noTries=0
		while(encryptedYet==0):
			encryptedYet=1
			try:
				p1 = self.run(['--encrypt'],create_fhs=['stdin','stdout','logger'])
				p1.handles['stdin'].write(message)
				p1.handles['stdin'].close()
	
				ciphertext = p1.handles['stdout'].read()
				p1.handles['stdout'].close()
					
				loggertext = p1.handles['logger'].read()
				p1.handles['logger'].close()
	
				# process cleanup
				p1.wait()
				status=1
				print "Message successfully encrypted"
			except IOError,b:
				status=0
				print b.args
				print "------"
				print loggertext
				print "------"
				if(string.find(loggertext,'bad passphrase')>0):
					print "Bad passphrase"
					if (noTries==0):
						passphrase=getpass.getpass("Your passphrase (to sign): ")
						self.passphrase = passphrase
						encryptedYet=0
						noTries=1
					else:
						status=0
				elif(string.find(loggertext,'no indication')>0):
					print "The key %s  has not been validated by yourself" %(keyID)
					print "or by a nominated Certifying Authority"
					print "There is no evidence that the key really belongs to the owner"
				elif(string.find(loggertext,'public key not found')>0):
						
					print "The key %s  was not found in your local keyring" %(keyID)
					status=loggertext


				else:
					print "Error : Unable to encrypt due to unknown error"
					print loggertext
					status=loggertext
			except:
					print "Error : Unable to encrypt due to unknown error"
					print loggertext	
					status=loggertext
					
			#print ciphertext
			return (status,ciphertext)


def wagLog(logName,logText):
	"add to log - mail,....."
	try:
		file=open(logFolder+"/"+logName+".log","a")
		file.write(logText)
		file.close()
	except:
		print "Error in writing to mail.log file\n"
		print sys.exc_type, ":", sys.exc_value
	   	
# configure 
keyServer='www.keyserver.medicine.net.au'
# setting default keyserver currently needs to be done within gpg config
smtpServer='medicineau.net.au'
wtServer="http://www.keyserver.medicine.net.au/wagtail/wagtailServer.php?email="
keyholdersFile="keyholders.wt"
logFolder="logs"
localNetwork="127"
smtpIP="localhost"
smtpPort=8023


gnupg = wtKeysClass()

#This is the 2.2 way of running asyncronous servers
server = OurServer((smtpIP, smtpPort),
                   (None, 0))
try:
    asyncore.loop()
except KeyboardInterrupt:
    pass
