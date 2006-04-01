"""processes complete summary rtf files from a popular oz EMR export. input is stdin, output is stdout plain text"""


import os, sys
import string
import StringIO

def rtf2plain(input_s, out =None , write_all = True):
	if not out:
		out = StringIO.StringIO()
	
	if input_s is None:
		input_s = ''
	if type(input_s) is str:
		input_s = StringIO.StringIO(input_s)

	l = []
	for x in input_s:
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
	 
	   l = y
	   
	   #for z in y.split('\\plain'):
	   #	if len(z) and z[0] <> '\\':
	   #		l.append(z)
	   #	elif len(z):
	   #		z2 = z.split(' ')
	   #		if len(z2) > 1:
	   #			l.append(' ')
	   #			l.append( ' '.join(z2[1:]) )
		

	   l4.append( ''.join(l) )

	   
	   
	l5 = []
	for x in l4:
		l5.append( '\t'.join( x.split('\\tab')) )
		
	l6 = []
	for x in l5:
		l6.append(''.join( x.split('\\intbl\\row') ) )


	l7 = []
	for x in l6:
		n =  x.find('MS Sans')
		if n >= 0:
			o = x.find('}}')
			if o > n:
				x = x[o+2:]
		l7.append(x)
	
	l8 = [] 
	for x in l7:
		n = x.find('tf1an')
		if n >= 1:
			o = x.find('}}')
			if o > n:
				x = x[:n-1] + x[o+2:]
			continue
		l8.append(x)		

	l9 = []
	for x in l8:
		z = []
		for y in x:
			if ord(y) > 20:
				z.append(y)
		l9.append(''.join(z))

	start_found = False

		
	l10 = []
	for x in l9:
		n  -1
		while  n < len(x)-1:
			n = x.find('plain', n+1)

			if n>=0 :
				o =  x.find('s1', n)
				if o < 0:
					o = x.find('s2',n)
				if o >= 0  :
					x = x[:n] + '___'+x[o+4:]
			else:
				break
		l10.append(x)


	l11 = []
	for x in l10:
		l =  x.split('. ')
		l2 = []
		for y in l:
			z = y.split(' ')
			l2.append(y)
			if len(z) and len(z[-1]) > 3 and y[-1] <> '.':
				l2.append('.\n')
			elif len(y) and y[-1] <> '.':
				l2.append('. ')
		x = ''.join(l2)
		
		l11.append(x)

	for x in l11:
		if not start_found and not write_all:
			if x.find('COMPLETE RECORD') >= 0:
				start_found = True
			else:
				continue

		out.write( x)
		out.write('\n')

		
	
	s = None
	if out.__class__ == StringIO.StringIO:
		s = out.getvalue()
		
	return s

	
	
		 
if __name__=="__main__":
	rtf2plain( sys.stdin, sys.stdout)

