1.install gnumed
2.install omniORB
3.install omniORBpy
4.run omniidl -nc -I. on each of  PersonIdService.idl, HL7Version2_3.idl and  PersonIdTraits.idl



For each time the server needs starting

5.run omniNames -start 5002 -logdir /home/xxx/omnilog 
	where 5002 is port , and omniLog is a created directory.
	
	(FIXME note, may have problems if computer is a network computer and doesn't have
	a localhost localdomain default name.
	)

6. Run the PersonIdService.
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
		
		
		
7. run 'python ResolveIdComponent.py -gnumed'
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
  
         the dsn for the dbapi is in PlainConnectionProvider.py.
	 	I've set up by gm-dbowner password as pg.
	 the corbaloc NameService url is in ResolveIdComponent.py
         the NameService directory paths for gnumed and openemed is also there.

								  1




