#!/usr/bin/python
# this is a simple gnumed client installation script
import sys, os.path, os, py_compile, shutil
from os.path import join

def soft_delete (f):
    if os.access (f, os.W_OK):
        if os.path.isdir (f):
            shutil.rmtree (f, 1)
        else:
            os.unlink (f)


if os.getuid () != 0:
    print """
*** You are not root. This script won't work
"""
    sys.exit (-1)

path = os.path.dirname (sys.argv[0])
if len (path) > 0:
    os.chdir (os.path.dirname (sys.argv[0])) # try to get to our home directory

remove = 0
prefix = '/usr'
bindir = '/usr/bin'
sharedir = '/usr/share/gnumed'
docdir = '/usr/share/doc/gnumed'
mandir = '/usr/share/man/man1'
manifest = None

# grab the command line args
for i in sys.argv[1:]:
    if i[:7] == "PREFIX=":
        prefix = i[7:]
        bindir = join (prefix, "bin")
        docdir = join (prefix , "share", "doc", "gnumed")
        sharedir = join (prefix,  "share", "gnumed")
	mandir = join (prefix , "share", "man", "man1")
        
    if i[:7] == "BINDIR=":
        bindir = i[7:]
        
    if i[:7] == "DOCDIR=":
        docdir = i[7:]
        
    if i[:9] == "SHAREDIR=":
        sharedir = i[9:]

    if i == "MANIFEST=1":
        manifest = file ('MANIFEST', 'w')
    # manifests of installed files are useful for some packageing systems
    # such as RPM
    if i == "-h" or i == "--help":
        print """
The GNUMed installation script (UNIX only).
Options are
      PREFIX=x    -- installation prefix, default /usr
      BINDIR=x    -- gnumed command directory, default /usr/bin
      SHAREDIR=x  -- gnumed general files, default /usr/share/gnumed
      DOCDIR=x    -- documentation files, default /usr/share/doc/gnumed
      MANIFEST    -- flag, if 1 then a MANIFEST of installed files is written
      remove      -- reverses the function of this script
      """
        sys.exit (0)
    if i == "remove":
        remove = 1
    
if remove:
    soft_delete (join (bindir, 'gnumed'))
    soft_delete (sharedir)
    soft_delete (docdir)
    soft_delete (join ('/etc', 'gnumed.conf'))
    sys.exit (0)
                 
    
# do some dependency checking. Plagiarized from check_prerequistes.py

print "=> checking for Python module mxDateTime ..."
try:
    import mx.DateTime
    print "=> found"
except ImportError:
    print "ERROR: mxDateTime not installed"
    print "ERROR: this is needed to handle dates and times"
    print "ERROR: mxDateTime is available from http://www.egenix.com/files/python/"
    sys.exit(-1)
        
print "=> checking for Python module pyPgSQL ..."
try:
    import pyPgSQL.PgSQL
    print "=> found pyPgSQL"
except ImportError:
    try:
        import pgdb
        print "=> found pgdb"
    except ImportError:
        try:
            import psycopg
            print "=> found psycopg"
        except ImportError:
            print "ERROR: no Python-postgres binding found"
            print "ERROR: this is needed to access PostgreSQL"
            print "ERROR: pyPgSQL is available from http://pypgsql.sourceforge.net"
            sys.exit(-1)

print "=> checking for Python module wxPython ..."
import os
if os.getenv('DISPLAY') is None:
    print "WARNING: cannot check for module wxPython"
    print "WARNING: you must run this in a GUI terminal window"
else:
    try:
        import wxPython.wx
        print "=> found"    
    except ImportError:
        print "ERROR: wxPython not installed"
        print "ERROR: this is needed to show the GnuMed GUI"
        print "ERROR: wxPython is available from http://www.wxpython.org"
        sys.exit(-1)
	print "=> found"

print "=> making directories"
if not os.access (bindir, os.F_OK):
    os.makedirs (bindir, 0755)
print "=> done"

print "=> installing files"

def process (fr, to):
    if not os.access (to, os.F_OK):
        os.makedirs (to, 0755)

    for i in os.listdir (fr):
        if i[-3:] == '.py':
            # it's source, compile it
            py_compile.compile (join (fr, i), join (to, i+ 'c'))
            if manifest:
                manifest.write ("%s\n" % join (to, i+'c'))
        else:
            if os.path.isdir (join (fr, i)):
                process (join (fr, i), join (to, i))
            else:
                shutil.copy (join (fr, i), join (to, i))
                if manifest:
                    manifest.write ("%s\n" % join (to, i))


process ('doc', docdir)
process ('man', mandir)
for i in ['python-common', 'wxpython', 'wxpython', 'business', 'locale', 'bitmaps']:
    process (i, join (sharedir, i))

print "=> done"

print "=> Creating gnumed.sh"
gnumed_sh = file (join (sharedir, 'wxpython', 'gnumed.sh'),'w')
gnumed_sh.write("""#!/bin/sh
export GNUMED_DIR=%s
python $GNUMED_DIR/wxpython/gnumed.pyc
""" % sharedir)
gnumed_sh.close ()
print "=> done"


print "=> Creating link in %s" % join (bindir, 'gnumed')
soft_delete (join (bindir, 'gnumed'))
os.symlink (join (sharedir, 'wxpython', 'gnumed.sh'), join (bindir, 'gnumed'))
print "=> done"

print "=> checking for system-wide config file"
if os.access ('/etc/gnumed.conf', os.F_OK):
    print "=> found, will leave as-is"
else:
    print "=> installing stock version"
    shutil.copy ('doc/gnumed.conf.example', '/etc/gnumed.conf')
    if manifest:
        manifest.write ("%s\n" % '/etc/gnumed.conf')

print """
Python client is now installed.
You can run it from %s/gnumed
Documentation is kept at %s/index.html
""" % (bindir, docdir)

if manifest:
    manifest.close ()
