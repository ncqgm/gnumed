path=../../server/sql/test-data
confpath=../../server/bootstrap
conf_file=bootstrap-test_data.conf
target=test_data
rm  test_data
touch test_data




python bootstrap-parse.py $confpath/$conf_file filelist-$conf_file

for y in `cat filelist-$conf_file`;do
	cat $path/$y >> $target
done	


echo psql -f $target -h 127.0.0.1 -Upostgres gnumed
psql -f $target -h 127.0.0.1 -Upostgres gnumed


