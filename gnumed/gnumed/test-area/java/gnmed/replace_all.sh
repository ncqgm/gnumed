# replaces  param1 with param2  in all java files , and the result ends as java.new files in java-work directory . Use commit_replace_all.sh to change java.new files to java files.

cp -R java java-work
for f in `find java-work/ -name "*.java"`;
do 
	sed -s s/$1/$2/g $f > $f.new;
done
