path=../../server/sql/test-data
confpath=../../server/bootstrap
conf_file=bootstrap-test_data.conf
user=gm-dbo
target=test_data
rm  test_data
touch test_data
#DB=gnumed_v3
DB=$1


python bootstrap-parse.py $confpath/$conf_file filelist-$conf_file

for y in `cat filelist-$conf_file`;do
	cat $path/$y >> $target
done	

echo
echo running test data
echo

echo psql -f $target -h 127.0.0.1 -U \"$user\" $DB

psql -f $target -h 127.0.0.1 -U "$user" $DB


