"""processes complete summary rtf files from a popular oz EMR export. input is stdin, output is stdout plain text"""


import os, sys
l = []
for x in sys.stdin:
   l.extend(x.split('\\line') )
l2 = []
for x in l:
   y = ' '.join (x.split(' ')[1:]) 
   l2.extend (y.split('\\par'))
l3 = []
for x in l2:
   
   if len(x) and ( x[0] == '\\' or x[0] =='d' ): 
	  y =  ' '.join(x.split(' ')[1:] )
	  if y.find('\\d')==0:
	    y = ''
	  l3.append(y)
   else:
   	l3.append(x)



l4 = []
for x in l3:
   y = ''.join( x.split('\\cell'))
 
   l = []
   for z in y.split('\\plain'):
   	if len(z) and z[0] <> '\\':
		l.append(z)
	elif len(z):
		z2 = z.split(' ')
		if len(z2) > 1:
		        l.append(' ')
			l.append( ' '.join(z2[1:]) )
   	

   l4.append( ''.join(l) )

   
   
l5 = []
for x in l4:
	l5.append( '\t'.join( x.split('\\tab')) )
	
l6 = []
for x in l5:
	l6.append(''.join( x.split('\\intbl\\row') ) )

start_found = False
for x in l6:
	if not start_found:
		if x.find('COMPLETE RECORD') >= 0:
			start_found = True
		else:
			continue
	
	print x


