
#changes import statements from client to Gnumed
sed -e "s/from client/from Gnumed/g"  -ibak `find ../.. -name "*.py"`
