
#changes elegant Gnumed symlink import statements to rough-as-guts client
# real path imports to suit cygwin proleterait python

sed -f cygwin.ed -ibak `find ../.. -name "*.py"`
