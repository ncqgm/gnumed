#restores the files recently sedded

for x in `find ../.. -name "*.pybak"` ;do
	cp  $x ${x%%pybak}py
done	

