#############################################################################
# gmKeys - Module to enable PKI management in python
# ---------------------------------------------------------------------------
#
# @copyright: Tony Lembke (tony@lemlink.com.au)
############################################################################
# This source code is protected by the GPL licensing scheme.
# Details regarding the GPL are available at http://www.gnu.org
# You may use and share it as long as you don't deny this right
# to anybody else.
# use GnuPGInterface which is available from http://py-gnupg.sourceforge.net/
# thanks to Frank J. Tobin, ftobin@neverending.org


#usage


#keyServer='medicine.net.au'
#smtpServer='localhost'
#import gmKeys
#gnupg = gmKeys.gmKeysClass()
#gnupg.list-keys()
#gnupg.search_local('dguest')
#gnupg.search_keyserver('dguest',keyServer)
#gnupg.send_message_manual(keyServer,smtpServer):
#gnupg.send_message('tony@lemlink.com.au','Me <tlembke@medicineau.net.au>','Get this one','Hi Tony','mypassphrase','medicine.net.au','localhost')

#TO_DO
#write a socket to connect to keyserver
#work out how to sign keys using GnuPGInterface

# required modules
import GnuPGInterface
# GnuPGInterface is available from http://py-gnupg.sourceforge.net/
import string
import re
import sys
import urllib


class gmKeysClass(GnuPGInterface.GnuPG):
	"Class to provide interface between GnuPG and Python"
	def __init__(self):
		GnuPGInterface.GnuPG.__init__(self)
		self.setup_my_options()

	def setup_my_options(self):
		self.options.armor = 1
		self.options.meta_interactive = 0
		self.options.extra_args.append('--no-secmem-warning')

	def encrypt_string(self, string, recipients):
		self.options.recipients = recipients   # a list!
		
		proc = self.run(['--encrypt'], create_fhs=['stdin', 'stdout'])
		
		proc.handles['stdin'].write(string)
		proc.handles['stdin'].close()
				
		output = proc.handles['stdout'].read()
		proc.handles['stdout'].close()

		proc.wait()
		return output
		
	def search_keyserver(self,searchTerm,keyServer):
		keyID=0
		# can't get GnuPGInterface to access keyserver so do through http
		searchString='http://'+keyServer+':11371/pks/lookup?op=index&search='+searchTerm
		
		theText=''
		try:
			page=urllib.urlopen(searchString)
			theText=page.read()
			page.close
		except:
			print "Unable to access keyserver %s" % keyServer

			
			
		if(theText!=''):
			# split into individual lines 
			keyList=string.split(theText,'\n');
			# regex to read each line
			p = re.compile(r'(^\w+)\s\s(\w+)/(.+)\"\>(\w+)\<(.+)\d\s(.+)&lt;(.+)\"\>(.+)\<')
			i=0;
			keyIDa=[0,1,2,3,4,5,6,7,8];
			
			for theString in keyList:
				if(string.find(theString,'pub')==0):   # only need pub keys
					m = p.search(theString)
					keyID= m.group(4)
					keyOwner= m.group(6)
					keyEmail=m.group(8)
					i=i+1
					keyIDa[i]=keyID
					print i,keyID,keyEmail,keyOwner
			if(i>0):
				keyToGet=input("Select Key to get (0 for none): ")
			else:
				print "Sorry, that key is not on the network keyserver %s." %keyserver
				print "Unable therefore to retreive key"
				keyToGet=0
			keyID=0
			if (keyToGet>0 and keyToGet<=i):
				keyID=keyIDa[keyToGet]
				print "I will retrieve Key %s,%s" % (keyToGet, keyID)
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
	
			else:
				print "No key selected"
		else:
			print "Keyserver could not be contacted"
		return keyID;
		
	def search_local(self,searchTerm):

		# create handles in p1
		p1=self.run( ['--list-keys'],create_fhs=['stdout'])
	
		# read handles
		keylist = p1.handles['stdout'].read()
		p1.handles['stdout'].close()
	
		# process cleanup
		p1.wait()
	
	
		# split into individual lines 
		keyList=string.split(keylist,'\n');
		# regex to read each line (q to read uid)
		p = re.compile(r'(^\w+)\s\s(\w+)/(\w+)\s(\w+)\W(\w+)\W(\w+)\W(.+)\s\<(.*)\>')
		q = re.compile(r'(^\w+)\s+(.+)\s<(.+)>')
	
		i=0;
		keyIDa=[0,1,2,3,4,5,6,7,8];
			
		for theString in keyList:
			
			if(string.find(theString,'sec')==0 or string.find(theString,'pub')==0):   # pub.sec keys
				m = p.search(theString)
				keyID= m.group(3)
				if(string.find(theString,searchTerm)>0):
					keyOwner= m.group(7)
					keyEmail=m.group(8)
					i=i+1
					keyIDa[i]=keyID
					print i,keyID,keyEmail,keyOwner
			# also need to check if search term in uid.
			# in which case keyID is the same as the last keyID
			if(string.find(theString,searchTerm)>0 and string.find(theString,'uid')==0 ):   # uid keys
				m=q.search(theString)
				if(keyIDa[i]!=keyID):   #if hasn't already been included
					keyOwner=keyOwner= m.group(2)
					keyEmail=m.group(3)
					i=i+1
					keyIDa[i]=keyID
					print i,keyID,keyEmail,keyOwner
		if(i==1):
			keyToGet=1
		elif(i>1):
			keyToGet=input("Select Key to get (0 for none): ")
		else:
			print "Sorry, that key is not in the local keychain."
			keyToGet=0
		keyID=0
		if (keyToGet>0 and keyToGet<=i):
			keyID=keyIDa[keyToGet]
		
		return keyID;
	
	def list_local(self):
		# create handles in p1
		p1=self.run( ['--list-keys'],create_fhs=['stdout'])

		# read handles
		keylist = p1.handles['stdout'].read()
		p1.handles['stdout'].close()

		# process cleanup
		p1.wait()


		# split into individual lines 
		keyList=string.split(keylist,'\n');
		# regex to read each line
		p = re.compile(r'(^\w+)\s\s(\w+)/(\w+)\s(\w+)\W(\w+)\W(\w+)\W(.+)\s\<(.*)\>')

		for theString in keyList:
			if(string.find(theString,'pub')==0):   # only need pub keys
				m = p.search(theString)
				keyID= m.group(3)
				keyOwner= m.group(7)
				keyEmail=m.group(8)
				print keyID, keyEmail, keyOwner
		
	def send_message_manual(self,keyServer,smtpServer):
		import smtplib
		import getpass
		toAddr=raw_input("Send a message to <email address>: ").strip()
		

		keyID=self.search_local(toAddr)
		if(keyID>0):
			keyFound=1
		if (keyFound==0):
			print "The key for %s is not available in local keychain" % toAddr
			print "Trying keyserver %s" % keyServer
			keyID=self.search_keyserver(toAddr,keyServer)
			
			if (keyID>0):
				keyFound=1
				
		
		
		if(keyFound==1):
			fromAddr=raw_input("From <email address>: ").strip()
			subject=raw_input("Subject: ").strip()
			message=raw_input("Message: ").strip()
			passphrase=getpass.getpass("Your passphrase (to sign): ")
			
			self.passphrase = passphrase
			self.options.recipients = [toAddr]
			#gnupg.options.always_trust=1
			encryptedYet=0
			noTries=0
			while(encryptedYet==0):
				encryptedYet=1
				try:
					p1 = self.run(['--sign','--encrypt'],create_fhs=['stdin','stdout','logger'])
					p1.handles['stdin'].write(message)
					p1.handles['stdin'].close()
	
					ciphertext = p1.handles['stdout'].read()
					p1.handles['stdout'].close()
					
					loggertext = p1.handles['logger'].read()
					p1.handles['logger'].close()
	
				# process cleanup
					p1.wait()
					okToSend=1
					print "Message successfully encrypted"
				except IOError,b:
					okToSend=0
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
							okToSend=0
							
							
						
					elif(string.find(loggertext,'no indication')>0):
						
							print "The key to %s has not been validated by yourself" %toAddr
							print "or by a nominated Certifying Authority"
							print "There is no evidence that the key really belongs to the owner"
							sendReply=raw_input("Send anyway [no]: ").strip()
							if(sendReply=='y' or sendReply=='yes'):
								gnupg.options.always_trust=1
								encryptedYet=0
					else:
						print "Error : Unable to encrypt due to unknown error"
						print loggertext
				except:
						print "Error : Unable to encrypt due to unknown error"
						print loggertext	
					
			#print ciphertext
		
			if(okToSend==1):
				# Add the From: and To: headers at the start!
				msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (fromAddr, toAddr,subject))
				msg=msg+ciphertext
	
				print "Connecting to SMTP server ......."
				try:
					server = smtplib.SMTP(smtpServer)
					server.set_debuglevel(1)
					server.sendmail(fromAddr, toAddr, msg)
					server.quit() 
					print "Message sent encrypted to %s" % toAddr
				except:
					print "Mail delivery error."
					print "Message not sent."
	def send_message(self,toAddr,fromAddr,subject,message,passphrase,keyServer,smtpServer):
		import smtplib
	
		# create handles in p1
		p1=self.run( ['--list-keys'],create_fhs=['stdout'])
	
		# read handles
		keylist = p1.handles['stdout'].read()
		p1.handles['stdout'].close()
	
		# process cleanup
		p1.wait()
	
	
		# split into individual lines 
		keyList=string.split(keylist,'\n');
		# regex to read each line
		#	p = re.compile(r'(^\w+)\s\s(\w+)/(\w+)\s(\w+)\W(\w+)\W(\w+)\W(.+)\s\<(.*)\>')
		keyFound=0
		for theString in keyList:
			if(string.find(theString,'pub')==0):   # only need pub keys
				if(string.find(theString,toAddr)>0):
					keyFound=1
		if (keyFound==0):
			print "The key for %s is not available in local keychain" % toAddr
			print "Trying keyserver %s" % keyServer
			keyID=self.search_keyserver(toAddr,keyServer)
			if (keyID>0):
				keyFound=1
				
		
		
		if(keyFound==1):
			self.passphrase = passphrase
			self.options.recipients = [toAddr]
			#gnupg.options.always_trust=1
			encryptedYet=0
			while(encryptedYet==0):
				encryptedYet=1
				try:
					p1 = self.run(['--sign','--encrypt'],create_fhs=['stdin','stdout'])
					p1.handles['stdin'].write(message)
					p1.handles['stdin'].close()
	
					ciphertext = p1.handles['stdout'].read()
					p1.handles['stdout'].close()
	
				# process cleanup
					p1.wait()
					okToSend=1
					print "Message successfully encrypted"
				except IOError,b:
					okToSend=0
					print b.args
					if(string.find(b.args[0],'131072')>0):
						print "The key to %s has not been validated by yourself" %toAddr
						print "or by a nominated Certifying Authority"
						print "There is no evidence that the key really belongs to the owner"
						sendReply=raw_input("Send anyway [no]: ").strip()
						if(sendReply=='y' or sendReply=='yes'):
							gnupg.options.always_trust=1
							encryptedYet=0
					else:
						print "Error : Unable to encrypt"
						print sys.exc_type," : ".sys.exc_value
				except:
						print "Error : Unable to encrypt"
						print sys.exc_type," : ".sys.exc_value		
					
			#print ciphertext
		
			if(okToSend==1):
				# Add the From: and To: headers at the start!
				msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (fromAddr, toAddr,subject))
				msg=msg+ciphertext
	
				print "Connecting to SMTP server ......."
				try:
					server = smtplib.SMTP(smtpServer)
					server.set_debuglevel(0)
					server.sendmail(fromAddr, toAddr, msg)
					server.quit() 
					print "Message sent encrypted to %s" % toAddr
				except:
					print "Mail delivery error."
					print "Message not sent."			


