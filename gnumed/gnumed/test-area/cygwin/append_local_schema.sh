path=../../server/sql/country.specific
confpath=../../server/bootstrap
target=all


for x in au de ;do
	ls $path$x;
	python bootstrap-parse.py $confpath/bootstrap-$x.conf filelist-$x

	for y in `cat filelist-$x`;do
		cat $path/$x/$y >> $target
	done	
done


