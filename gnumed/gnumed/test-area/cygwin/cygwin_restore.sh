#restores the files recently sedded
#BY SWAPPING

for x in `find ../.. -name "*.pybak"` ;do
	cp ${x%%pybak}py ${x%%pybak}tmp
	cp  $x ${x%%pybak}py
	mv ${x%%pybak}tmp $x
done	

