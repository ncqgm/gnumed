
from  wxPython.wx import *
import gmPG

class SimplePopupQueryResultWindow( wxPopupWindow):

    def __init__(self, parent, query,  maxColWidth= 30, style = wxSIMPLE_BORDER ):
        wxPopupWindow.__init__(self, parent, style)
	
        panel = wxPanel(self, -1)
        panel.SetBackgroundColour("#FFB6C1")
	try:
		backend = gmPG.ConnectionPool()
		db = backend.GetConnection('default')
		cursor = db.cursor()
		cursor.execute("commit")
		print "doing query", query
		cursor.execute(query)
		colcount = len( cursor.description)
		result = cursor.fetchall()
		cursor.execute("commit")
	except Exception,errorStr:
		print errorStr
		colcount = 1
		result = [ ['No result set'] ]

	print "simple popup got ", result
	maxwidth = []
	for i in xrange (0, colcount):
		maxwidth.append(0)

	# for each column, maximum width = lesser of global maximum column width or longest item length		
	for x in result:
		i = 0
		for item in x:
			itemLen = len(str(item))
			if itemLen > maxwidth[i]:
				if itemLen   < maxColWidth:
					maxwidth[i] = itemLen 
				else: 
				 	maxwidth[i] = maxColWidth
						
				 
			i += 1
				
	list = []
	for x in result:
		i = 0
		sublist = []
		extralines = []
		for item in x:
			 # remove any newline characters
			
			ss = str(item)
			l = ss.splitlines()
			ss = ' '.join(l)
			print "after new line removal ss = ", ss

			if len(ss) > maxwidth[i]:
			# handle overflow of maximum column width, multi-line fields 

				# hypenate at maxwidth	
				prev = 0
				k = maxwidth[i] 
				l =  []
				
				# start hyphenation block:
				# while the section is entirely within the string 
				#	check the section end boundary for 2 consecutive alphanumeric characters
				#	split with a '-' if present
				#	previous is the last character of the section + 1 ( python string operation assumes  y-1 for y in [x:y] )
					 
				while k < len(ss) -1:
					if ss[k-1].isalnum() and ss[k].isalnum() :
						k -=1
						l.append( ss[prev:k] )
						l.append('-')
					else:
						l.append(ss[prev:k])
					prev = k
					k += maxwidth[i]
				l.append(ss[prev:])

				# join up the hyphenated string
				ss = ''.join(l)	

				#end hyphenation code
						


				prev = 0
				# count the characters in all columns before this column
				for j in xrange(0, i):
					prev += maxwidth[j] +2
							
				# start of paragraph formatting for column
				s = ss[0: maxwidth[i] ]
				j = maxwidth[i] 
				k = 0
				sub = ''
				while not j > len(ss):
					print "ss = ", ss, " sub = ", sub
					sub = ss[ j : j + maxwidth[i]  ]
					spaces = prev
			
					# spaces = space in previous columns 
					#		minus count of  previous paragraph characters in other columns (extralines)
					if len(extralines) > k:
						spaces -= len(extralines[k])
					else:
						extralines.append('')

					extralines[k] +=( ' ' * spaces)
					extralines[k] +=( sub.ljust(maxwidth[i] + 2) )
					j += maxwidth[i] 
					k += 1
			else:
			#handle normal single line field
				s = ss.ljust(maxwidth[i])
			i += 1
			sublist.append(s)
			
		substr = '  '.join(sublist)
		if len(extralines) > 0  :
			substr+=('\n')
			substr+=( '\n'.join(extralines) )

		list.append(substr)


	print "list to join = " ,list
	allstr = '\n'.join(list)
	#
	# end of multiline column formatting


        st = wxStaticText(panel, -1,
				allstr
                          ,
                          pos=(10,10))
	font = wxFont(9, wxMODERN, wxNORMAL, wxNORMAL)
	st.SetFont(font)	
        sz = st.GetBestSize()
        panel.SetSize( (sz.width+20, sz.height+20) )
        self.SetSize(panel.GetSize())
 
