import sys
import re

header = re.compile("^\[(.*)\]$")
list_mark= re.compile(".*\$(.*)\$.*")
m = {}
inList = False
key = None
for l in file(sys.argv[1]):
	res =  header.match(l)
	if res:
		print l
		section = res.group(1)
		w  = section.split(' ')
		service_name=' '.join(w[1:])
		is_typed_section= w[0] in ['service', 'database', 'server']
		if is_typed_section:
			m[w[0]] = m.get(w[0], {})
			m[w[0]][service_name] = {}

		
	else:
		mark= list_mark.match(l)
		if mark:
			oldKey = key
			key=mark.group(1)
			inList = not inList
			if not inList:
		
				if is_typed_section:
					m[w[0]][service_name] =m[w[0]].get(service_name,{})
					m[w[0]][service_name][key]= list
				else:
					m[section]=m.get(section,{}) 
					m[section][key] = list
			else:
				list=[]
				continue
	if inList:
			list.append(l.strip())

			
				
for k,v in m.items():
	print k,v
	print


l = m['installation']['services']
listOrdService= ['core'] + l

all= {}
all.update(  m['service'])
all.update(  m['database'])	

for service in listOrdService:
	print service

for service in listOrdService:
	print all[service].get('schema',[])
		 

f2 = file(sys.argv[2], 'w')

for service in listOrdService:
	for x in all[service].get('schema',[]):
		f2.write(x)
		f2.write('\n')
f2.close()


