"""change the twikidir and targetdir to suit. Backup first."""
twikidir = '.'
targetdir = './moin'
import os
import sys
import os.path
import traceback 
import re
import string
verbatim = 0
def twikimoin_format(l):
	l = screen_unprintable(l)
	l = meta_topic(l)
	l = match_verbatim(l)
	if verbatim:
		return l	
	l = match_anchor(l)
	#l = match_anchorlink1(l)
	l = match_link(l)
	l = match_table(l)
	l = match_italic(l)
	l = match_br(l)
	l = match_bold(l)
	l = match_monospace(l)
	l = match_heading(l)
	#l = twiki_spaced_wikiword(l)

	return l

def match_monospace(l):
	EQ1, MONO  = 1, 2
	monospace = []
	lastx = None
	state =  0
	for x, i in zip(l, xrange(0,len(l))):
		if state == 0 and x == '=':
			state=EQ1
		elif state == EQ1 and x not in string.whitespace:
			state=MONO
			start = i-1
		elif state ==MONO and x == '=' and lastx not in string.whitespace:
			end = i
			monospace.append((start, end))
			state = 0
		lastx = x
	
	monospace.reverse()
	for start, end  in monospace:
		l =  l[:end] + "`" + l[end+1:]
		l =  l[:start] + "`" + l[start+1:]
		
	return l		
colorchoice =0
def match_table(l):
	colors = ["<#FF8080>", "<#80FF80>", "<#8080FF>"]
	l2 = l.strip()
	if l2 and l2[0] == '|' and l2[-1] == '|':
		global colorchoice
		colorchoice += 1
		s = '||'+colors[colorchoice % len(colors)] 
		l = s.join(l.split('|')).strip()[:-len('<#FF8080>')]
	return l	
		

def match_br(l):
	n = l.find('<br>')
	while n > -1:
		l = l[:n] +'[[BR]]' + l[n+len('<br>'):]
		n = l.find('<br>')
	return l

def match_bold(l):
	BOLD1=1
	NONWS1 = 2
	BOLDTEXT = 3
	BOLD2= 4
	state = 0
	markers = []
	i = 0
	lastx = None
	for x,i  in zip( l, xrange(0, len(l))):
		if state == 0:
			if x == '*':
				state = BOLD1
		elif state == BOLD1:
			if x not in string.whitespace:
				state= BOLDTEXT
				start = i-1
				markers.append(start)
		elif state == BOLDTEXT:
			if x == '*' and lastx not in string.whitespace:
				end = i
				markers.append(end)
				state = 0
		lastx = x	
	markers.reverse()

	for pos in markers:
		l = l[:pos] + "'''" + l[pos+1:]
	return l	
				
			

def meta_topic(l):
	if l.find("%META") == 0:
		if l.find("PARENT") > 0:
			i = l.find("name=")
			if i > 0:
				state = 0
				while i < len(l):
					i += 1
					if state == 0:
						if l[i] in "'\"":
							state =1
							w= []
					elif state ==1:
						if l[i] in "'\"":
							return " ''''back to: " +"".join(w) + "''''"
						else:
							w.append(l[i])
							
		return ""					
	return l

def match_italic(l):
	FIRSTDASH = 1
	IN_UNDERLINED= 2
	ENDALNUMDASH = 3
	state =0
	start = 0
	i = -1
	lastx = None
	end = None
	change = [] 
	for x in l:
		i += 1
		if state == 0:
			if x == '_':
				state =FIRSTDASH
				start = i
		elif state == FIRSTDASH:
				state = IN_UNDERLINED 
		elif state == IN_UNDERLINED:
			if x == '_':
				end = i 
				change .append( (start, end))
				state = 0

		lastx = x
					
	if not change is []:
		change.reverse()
		for (s, e) in change:
			l = l[:s] + "''" + l[s+1:e] + "''" + l[e+1:]
		
	return l	
		
	
	

def screen_unprintable(l):
	return  "".join([ x for x in l if x in string.printable])

def match_verbatim(l):
	i =  l.find("<verbatim>") 
	if i>= 0:
		l = l[:i] + '{{{' + l[i+len("<verbatim>"):]
		verbatim = 1
	
	i = l.find("</verbatim>")
	if i >=0:
		l = l[:i] + '}'+'}'+'}' + l[i+len("</verbatim>"):]
		verbatim = 0
	
	return l	
	

re_heading = re.compile("\s*(?P<level>(\-\-\-[\+]+)|(\+\+\++))(?P<heading>.+)")
def match_heading(l):
	mobj = re_heading.match(l)
	if mobj:
		n = len ([y for y in mobj.group("level") if y == '+'])
		title = mobj.group('heading')
		# don't nest links and headings
		if title.find('[') >=0 and  title.find('[') < title.find(']'):
			return title
		l = n * "=" +" "+ mobj.group("heading") + " " + n * "="
		print l
	return l

def match_anchor(l):
	l3 = l
	if l.lstrip() and  l.lstrip()[0] is '#':
		l2 = l.lstrip()[1:]
		l3 =  "[[Anchor("+l2.split(' ')[0].strip()+")]]"
	return l3

	
def capitalizeUnlessUpper(x):
	x= ''.join([ y for y in x if y  in string.letters + string.digits])
	
	capitals = 0
	for y in x:
		if y in string.uppercase:
			capitals += 1
	if capitals == 0:
		return x.capitalize()
	return x
		


def match_link(l):
	OUT = 1
	L1 = 2
	L2= 3
	R2= 4
	SEC = 5
	R1 = 6
	content = []
	state = OUT
	first , second = None, None
	i = 0
	for x in l:

		if state == OUT:
			if x == '[':
				upperCount = 0
				state = L1
				start = i
		elif state == L1:
			if x == '[':
				state = L2
				first, second =[],[]
			else:
				state = OUT
				
		elif state == L2:
			if x <> ']'  :
				first.append(x)
				if x in string.uppercase:
					upperCount += 1
			else:
				state = R2
		elif state == R2:
			if x == ']':
				end = i + 1

				if second <> None:
					second = ''.join(second)
					
				first = ''.join(first).strip(' ')

				#check for wiki phrase
				print "upperCount =", upperCount

				if (first.upper() == first or upperCount < 2)  and first[:4].lower() not in[ 'http', 'mail', 'ftp:']  and second :
					first = first + ' ' + second
					second =  first
					first = ''.join( [ capitalizeUnlessUpper(x) for x in first.split(' ')] )
					
					try:
						b = len(first)
						while  b > 0 and  (first[b-1] in string.punctuation + string.whitespace ):
							b -= 1
						first = first[:b]	
					except:
						traceback.print_exc()
						print "b", b , "first", first
						sys.stderr,write(   "b" + str( b) + " first" + str(first) )
						
					
					
				content.append((first, second, start, end))

				state  = OUT			
			elif x == '[':
				state = SEC
				second = []
		elif state == SEC:
			if x == ']':
				state = R2 
			else:
				second.append(x)

		i += 1
		
	print "Links for " , l
	print " Are ", content
	content.reverse()
	
	prefixes =  ['http', 'mail', 'ftp:', 'anchor']
	for first, second, start, end in content:
		found = [x for x in prefixes if first.lower().find(x) == 0]
		if not found:
			if first.find('#') >= 1:
				first="Self:"+first
			else:	
				if not second:
					second = first
			
				if not first[0:1] == '#':
					first = ''.join([ capitalizeUnlessUpper(x) for x in first.split(' ')])

				first = ":"+first+":"


		if second:
			frag = first + " "+ second 
		elif not 'anchor' in found and not first[:1].isupper():
			frag = first + " "+ first
		else:
			frag = first

		if 'anchor' in found:
			frag = '['+frag+']'

		if frag.find('Self') < 0:
			frag = '['+frag+']'

		l = l[:start]  + frag   + l[end:]
	
	print "l is now ", l

	return l
#main

try:
	os.mkdir(targetdir)
except:
	print "error trying to make " , targetdir
	print sys.exc_info()[0]


l = os.listdir(twikidir)

for f in l:
	if f[-3:] == 'txt':
		print f
		prefix = f[:-4]
		print prefix
		try:
			path = os.path.join(targetdir, prefix)
			print path
		except:
			print "error creating path from ", targetdir, prefix
			print sys.exc_info()[0]
			continue
		try:
			os.mkdir(path)
		except:
			print "error creating ", path


		try:
			revisions = os.path.join(path, "revisions")
			os.mkdir(revisions)
		except:
			print "error creating ", revisions
		try:	

			one = os.path.join(revisions, "00000001")
			targ = file(one, "w+")
			for l in file(f):
				l = twikimoin_format(l)
				#continue
				targ.write(l)
				targ.write('\n')

		except:
			print sys.exc_info()[0]
			traceback.print_tb( sys.exc_info()[2] )

		try:
			targ2 = file(os.path.join(path, "current"), "w+")
			targ2.write("00000001\n")
		except:
			print sys.exc_info()[0]
			traceback.print_tb( sys.exc_info()[2] )

	
