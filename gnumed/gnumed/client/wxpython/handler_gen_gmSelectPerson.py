from  handler_generator import generator

gen = generator()

import fileinput

lines = fileinput.input('gmSelectPerson.py')
list = []
for l in lines:
	pair = gen.get_name_type_for_line(l)	
	if pair <> None:
		list.append(pair)

gen.process_list(list)

gen.print_single_class('SelectPersonHandler')

