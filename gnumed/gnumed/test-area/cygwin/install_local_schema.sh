path=../../server/sql/country.specific/
confpath=../../server/bootstrap



for x in au de ;do
	ls $path$x;
	python bootstrap-parse.py $confpath/bootstrap-$x.conf filelist-$x

	for y in `cat filelist-$x`;do
		echo psql -f $path$x/$y gnumed
		psql -f $path$x/$y gnumed
	done	
done


