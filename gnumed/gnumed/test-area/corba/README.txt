1.install gnumed
2.install omniORB
3.install omniORBpy  
 
 	3. can be done using make , install and copying contents of ../{library for python}/site-packages recursively into /usr/lib/python2.2/site-packages, for those with demented distributions that want to foil default gnu configure/make/install for most unix packages.
	
	2 + 3 can also be done by using rpm -ta on the omni tgz packages and installing the binary rpms ( for those with rpm based packaging systems ). 


4.run omniidl -nc -I. on each of  PersonIdService.idl, HL7Version2_3.idl and  PersonIdTraits.idl

or  sh gen_stubs.sh  , to run omniidl on all the stubs here.



5.run omniNames -start 5002 -logdir /home/xxx/omnilog 
	where 5002 is port , and omniLog is a created directory.
	
	(FIXME note, may have problems if computer is a network computer and doesn't have
	a localhost localdomain default name.
	)

6. SERVER: Run the PersonIdService.
	a. run the gnumed PersonIdServiceWrapper server. 
		Just run 
		python StartIdentificationComponent.py 
		
		run help.py for parameters to server.
	
	(optionally)
	b. the open emeds PIDS service.
		- 
		- the following should be in the PIDS server 
		log output.
		INFO  gov.lanl.Utility.NameService  - us/nm/state/doh/Pilot Bound to NameService as us/nm/state/doh/Pilot
		
		- may have problems when connected to internet.
		
		
		
7. TEST-SUITE CLIENT: run 'python ResolveIdComponent.py -gnumed'
		to test the gnumed PersonIdService.
		This will go through the component tests,
		in Test...  (SequentialAccess, IdentifyPerson, IdMgr, ProfileAccess so far done, except for IdMgr merge and unmerge ids function)
		

(optional) run 'python ResolveIdComponent.py' will attempt
to connect to the open-emeds PIDS service if it is running.


8. What does this show?

Gnumed is easily extensible and can be adapted to imitate standard protocols such
as corbamed. 

Gnumed can be the backend for clients written in other languages which
call a corba med interface.


Important external parameters:
  connection strings are :
  
        a. the dsn for the dbapi is in PlainConnectionProvider.py.
	 	I've set up  database gnumed, user gm-dbowner,  password as pg.
		
	b. the corbaloc NameService url is in ResolveIdComponent.py
		corbaloc:iiop:localhost:5002/NameService
        c. the NameService directory paths for gnumed and openemed is also there.		'gnumed' and 'us/blah..blah/Pilot'
	
								  1




