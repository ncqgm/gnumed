# To demonstrate functions of gmKeys, which should be in the same directory
# or in the sys.path


#------------------------------------------
#Config options 
keyServer='medicine.net.au'
# usu config would be smtpServer='localhost'
smtpServer='medicineau.net.au'
# -----------------------------------------


import gmKeys,sys


gnupg = gmKeys.gmKeysClass()

if (sys.argv[1]=="list-keys"):
	gnupg.list_local()
			
elif(sys.argv[1]=="search-keys"):
	
	try:   
		searchTerm=sys.argv[2];
	except IndexError:     # if they forget to put string in command line
		searchTerm=raw_input("Enter string to search for: ")
		
	if(searchTerm==''):
		print "You need to specify a key to search for"
	else:
		gnupg.search_local(searchTerm)
		
					
elif(sys.argv[1]=="send"):	
	gnupg.send_message_manual(keyServer,smtpServer)
	
elif(sys.argv[1]=="search-keyserver"):	
	try:
		searchTerm=sys.argv[2];
	except IndexError:     # if they forget to put string in command line
		searchTerm=raw_input("Enter string to search for: ")
		
	if(searchTerm==''):
		print "You need to specify a key to search for"
	else:
		gnupg.search_keyserver(searchTerm,keyServer)	
else:
	print "Usage\nYou need to specify a command"
	print """Available commands are
	list-keys (list keys on local keychain)
	search-keys [search string] (search keys on local keychain)
	search-keyserver [search string] (search keys on keyserver)
	send (send an encrypted message)
	"""



