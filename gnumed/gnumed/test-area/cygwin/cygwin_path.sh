
#changes import statements from Gnumed to client
sed -e "s/from Gnumed/from client/g" -ibak `find ../.. -name "*.py"`

