from create_pgdb import Parser as Parser


if __name__ == "__main__":

	import sys
	print sys.argv

	p = Parser(sys.argv[1])
	start = None
	if len(sys.argv) > 2:
		start = int(sys.argv[2])

	if len(sys.argv) > 3:
		next = start + int(sys.argv[3])
		if next > p.get_numrecs() :
			next = p.get_numrecs()
	else:
		next = p.get_numrecs()


	print start, next
	if start is not None:	
		for i in xrange(0, start):
			p.next()

		for i in xrange(start,next):
			d,m = p.next(True)
			for x in d:
				for y in x:
					print y
			print "-"* 100
	
