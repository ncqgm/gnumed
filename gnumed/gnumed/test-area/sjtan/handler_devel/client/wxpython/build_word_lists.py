
import re
import string
import sys
import cPickle

str = '\A\W*(?P<word>\w+)\W*'

class Search:
	def __init__(self, filename):
		self.filename = filename
		
	def build_word_table(self):	
		prog = re.compile(str)
		f = file(self.filename, 'r')
		i = 0
		map_word_lines = {}
		line_no_file_positions= {}
		while(1):
			line_no_file_positions[i] = f.tell()
			line = f.readline()
			if line == '':
				break
			words = string.split(line)
		#	print
		#	print words
			lower_words = []
			for x in words:
				result = prog.match(x)
				if result<> None:
					word = result.group('word').lower()
					lower_words.append(word)
					
		#	print lower_words
			for word in lower_words:
				list = map_word_lines.get(word, [])
				if i not in list:
					list.append(i)
					map_word_lines[word] = list
					#print word, list	
			i = i + 1
			#sys.stderr.write('.')
		
		self.map_word_lines = map_word_lines
		return map_word_lines, line_no_file_positions	



	def drill_up(self, line_no, file_positions):
		str = '(?P<wspace>\s*)(?P<term>.*)\s*'
		tabs_find_prog = re.compile(str)
		f = file(self.filename, 'r')
		terms = []
		i = line_no 
		tabs = '\t\t\t'
		init = 1	
		while init or len(tabs) > 2:
			if i < 0:
				break
			f.seek(file_positions[i])
			line = f.readline()
			re_tabs_term = tabs_find_prog.match(line)
			#print "checking out line", line	
			prev_tabs = re_tabs_term.group('wspace')
			prev_term = re_tabs_term.group('term')
			if init :
				init = 0
				tabs = prev_tabs
				terms.append(prev_term)
				continue
				
			if len(prev_tabs) < len(tabs):
				terms.append(prev_term)
				tabs = prev_tabs
			i = i - 1
		terms.reverse()

		for i in xrange(0, len(terms)): 
			terms[i] = terms[i].strip()
			
		return terms

	def find_block( self,  aterm):
		str = '(?P<tabs>\s\s)(?P<term>\w+)(?P<rest>.*)'
		str_inner = '(?P<tabs>\s+)(?P<term>.*)\s*'
		block_head_prog = re.compile(str, re.I)
		block_inner_prog = re.compile(str_inner, re.I)
		f = file(self.filename, 'r')
		search_head = 1
		search_end = 2
		state = search_head
		lines = []
		for line in f:
			if state == search_head:
				result = block_head_prog.match(line)
				if result <> None:
					term = result.group('term')
					if term.strip().lower() == aterm.strip().lower():
						print "found term=", term , "rest =", result.group('rest')
						rest = result.group('rest')
						s = "".join( (term, rest))
						head_tabs = result.group('tabs')
						lines.append( ( head_tabs, s ) )
						state = search_end
				continue
			if state == search_end:
				result = block_inner_prog.match(line)
				if result <> None:
					tabs = result.group('tabs')
					if len(tabs) <= len(head_tabs):
						break
					lines.append( (tabs, result.group('term')))	
		return lines			

	def drill_up_block(self, lines, term):
		searching = 1
		drilling = 2
		state = searching
		terms = []
		for j in xrange(  1 , len(lines)+1): 
			i = len(lines) - j
			#print i, len(lines)
			#print lines[i]
			lterm = lines[i][1]
			if state == searching:
				#print "comparing ", lterm , " with ", term
				if lterm == term:
					#print "equal"
					state = drilling
					terms.append(term.strip())
					tabs = lines[i][0]
					continue
			if state == drilling:
				if len(lines[i][0]) == len(tabs) -1:
					term = lines[i][1].strip()
					words = term.split()
					if len(words) > 4:
						term = " ".join( words[0:4])
					else:
						term = " ".join( words)
						
					terms.append(term)
					tabs = lines[i][0]
					
		terms.reverse()
		#print "terms = ", terms
		return terms

	def get_leaf_and_children( self,  words):
		word_str = "([\W|\s]*([.|\w]+)[\W|\s])*"
		prog = re.compile( word_str, re.I)

		before = 1
		inside = 2
		results = []
		for x in words:
			lines = self.find_block( x)
			#print x, " has blocksize", len(lines)
			other_words = []
			other_words.extend(words)
			other_words.remove(x)
			#print "word and other words----", x, other_words
			state = before
			first = 0
			result = []
			if len(lines) > 0:
				result.append( "".join( (lines[0][0], lines[0][1]) ) )
			for y in other_words:
			    for tabs, term in lines:
				if  state == before:
					terms = term.split()
					#*result = prog.match( term)
					#index = result.lastindex
					#print "result = ", result.groups(range(0, index))
					short_list = filter( lambda x: x.lower() == y.lower(), terms[0: len(terms)-1])
					if len(short_list) > 0:
						state = inside
						first = 1
						level_tabs = tabs
						

				if state == inside:
					if len(level_tabs) > len( tabs):
						state = before
						continue
					if not first and len(level_tabs) == len(tabs):
						state = before
						continue
					if first and len(level_tabs) < len( tabs):
						first = 0
						
					result.append( "".join( (tabs, term) ) )
			results.append(result)		
		return results
		
	def find_drilled_up_reference(self, words):
		results = []
		for x in words:
			lines = self.find_block(x)
			other_words = []
			other_words.extend(words)
			other_words.remove(x)
			for y in other_words:
				for tabs, term in lines:
					prefix = y[0: 8 * len( y ) / 10]
					if term.lower().find(y.strip().lower()) >= 0:
						 results.append(",".join( self.drill_up_block(lines, term) ))
		return results				 

	def find_line_numbers_with_multiple_words(self,words, word_line_numbers_map):
		cumulative_map = {}
		for term in words:
			list_line_no = word_line_numbers_map.get(term, [])
			#print term, " is on lines ", list_line_no
			for line_no in list_line_no:
				terms= cumulative_map.get(line_no, [])
				terms.append(term)
				cumulative_map[line_no] = terms
			
		result = {}
		for k,v in cumulative_map.items():
			if len(v) > 1:
				result[k] = v
		return result		
		
						 
					
	def main(self):
		
		if len(sys.argv) > 2 and sys.argv[2] == 'build':
			amap, line_no_file_positions = self.build_word_table()
			
			cPickle.dump(amap,  file( self.filename+'_map', 'w'))
			cPickle.dump(line_no_file_positions,  file( self.filename+'_pos', 'w') )

		else:
			amap = cPickle.load( file( self.filename+'_map', 'r'))
			line_no_file_positions = cPickle.load( file( self.filename+'_pos', 'r') )

		self.amap = amap
		self.line_no_fille_positions = line_no_file_positions
		while(1):
			phrase = raw_input('enter phrase to search for:')
			self.get_results(phrase)



	def get_results(self, phrase):		
		str = '(?P<wspace>\s+)(?P<term>.*)\s*'
		tabs_find_prog = re.compile(str)
		amap = self.amap 
		line_no_file_positions = self.line_no_file_positions

		
		words = string.split(phrase)
		sys.stderr.write("looking at ")
		for x in words:
			sys.stderr.write ('('+x+')')

		names = amap.keys()
		names.sort()
		focus = 0
		synonyms = []
		for y in words:
			some_names = filter( lambda x: x.lower().startswith(y.lower().strip()) , names)
			exact = filter( lambda x: x.lower().strip() == y.lower().strip() , names)
			
			sys.stderr.write( "y is like %s\n "% ",  ".join( some_names))
			if len(some_names) == 1 or exact <> [] :
				focus = 1
				break
			synonyms.append(some_names)
		if not focus:

			return	synonyms
	
		words = map( string.lower, words)
		words = map( string.strip, words)
		#print "words = ", words
		all_results = []

		sys.stderr.write("BLOCK START AND SUB\n")
		results = self.find_drilled_up_reference(words)
		for x in results:
			print x
		
		all_results.extend(x)
		
		
		#for k,v in cumulative_map.items():
		#	if len(v) > 1:
		#		sys.stderr.write(  "on line %d , %s\n"% (k, v))

		line_numbers_with_multiple_words = \
			self.find_line_numbers_with_multiple_words(words, amap)

		sys.stderr.write("SINGLE LINE, INTERSECTING WORDS\n")		
		result = []
		for k,v in line_numbers_with_multiple_words.items():
			terms = self.drill_up(line_no = k, file_positions = line_no_file_positions)
			print ", ".join(terms)
			result.append( ", ".join(terms))

		all_results.extend(result)	
		

		
		sys.stderr.write("LEAF AND CHILDREN\n")

		results = self.get_leaf_and_children( words)
		for x in results:
			print
			for y  in x:
				print y	
		for x in results:
			all_results.extend(x)
		
		sys.stderr.write("WHOLE BLOCKS\n")

		for x in words:
			lines = self.find_block(x)
			for tabs, term in lines:
				print tabs, term
				result.append(''.join( tabs,term)))
		
		all_results.append(result)
		
		return all_results		


if __name__=='__main__':
	s = Search(sys.argv[1])
	s.main()
							

						

