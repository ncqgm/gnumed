# A Python class to replace the PSQL command-line interpreter
# NOTE: his is not a full replacement for the interpeter, merely
# enough functionality to run gnukmed installation scripts
# Copyright (C) 2003 GNUMed developers
# Licence: GPL

import sys, os, string, re
sys.path.append ('/home/ian/gnumed/gnumed/client/python-common')
import gmLog


class Psql:

    def __init__ (self, conn):
        """
        db : the interpreter to connect to, must be a DBAPI compliant interface
        """
        self.conn = conn
        self.vars = {'ON_ERROR_STOP':None}

    def match (self, str):
        match = re.match (str, self.line)
        if match is None:
            ret = 0
        else:
            ret = 1
            self.groups = match.groups ()
        return ret

    def log (self, level, str):
        gmLog.gmDefLog.Log (level, "%s: line %d: %s" % (self.filename, self.lineno, str)) 
        
    def run (self, filename):
        """
        filename: a file, containg semicolon-separated SQL commands
        """
        self.cmd = ''
        self.lineno = 0
        self.filename = filename
        instring = 0
        bracketlevel = 0
        if os.access (filename, os.R_OK):
            self.file = file (filename)
        else:
            self.log (gmLog.lErr, "cannot open file")
            return 1
        for self.line in self.file.xreadlines ():
            # remove comments
            comment = string.find (self.line, '--')
            if comment >= 0:
                self.line = self.line[:comment]
            if len (self.line) > 0:
                # process \ commands
                if self.match (r"^\\echo (.*)"):
                    self.log (gmLog.lInfo, self.groups[0])
                elif self.match (r"^\\qecho (.*)"):
                    self.log (gmLog.lInfo, self.groups[0])
                elif self.match (r"^\\q"):
                    self.log (gmLog.lWarn, "script terminated by \\q")
                    return 0
                elif self.match (r"^\\set (\S+) (\S+)"):
                    self.vars[self.groups[0]] = self.groups[1]
                    if self.groups[0] == 'ON_ERROR_STOP':
                        self.vars['ON_ERROR_STOP'] = int (self.vars['ON_ERROR_STOP'])
                elif self.match (r"^\\unset (\S+)"):
                    self.vars[self.groups[0]] = None
                elif self.match (r"^\\connect.*"):
                    self.log (gmLog.lErr, "\\connect not yet supported in scripts")
                elif self.match (r"^\\lo_import.*"):
                    self.log (gmLog.lErr, "\\lo_import not yet supported")
                    # no sense to continue here
                    return 1
                elif self.match (r"^\\copy .* to '(\S+)' .*"):
                    self.log (gmLog.lErr, "\\copy to not implemented")
                    return 1
                elif self.match (r"^\\copy .* from '(\S+)' .*"):
                    copyfile = self.groups[0]
                    try:
                        copyfd = file (os.path.join (os.path.dirname (self.filename), copyfile))
                    except error:
                        self.log (gmLog.lErr, error)
                        return 1
                    self.line = self.line[1:] # lop off leading slash
                    self.line.strip ()
                    self.line.replace ("'%s'" % copyfile, 'stdin')
                    # now we have a command that the backend understands
                    copyline = 0
                    try:
                        curs = self.conn.cursor ()
                        # send the COPY command
                        curs.execute (self.line)
                        # send the data
                        for i in copyfd.xreadlines ():
                            curs.execute (i)
                            copyline += 1
                        self.conn.commit ()
                        curs.close ()
                    except StandardError, error:
                        gmLog.gmDefLog.Log (gmLog.lErr, "%s: %d: %s" % (copyfile, copyline, error))
                        if self.vars['ON_ERROR_STOP']:
                            return 1
                elif self.match (r"^\\i (\S+)"):
                    # create another interpreter instance in same connection
                    Psql(self.conn).run (os.path.join (os.path.dirname (self.filename), self.groups[0]))
                elif self.match (r"^\\encoding.*"):
                    self.log (gmLog.lErr, "\\encoding not yet supported")
                elif self.match (r"^\\(.*)"):
                    # most other \ commands are for controlling output formats, don't make
                    # much sense in an installation script, so we gently ignore them
                    self.log (gmLog.lWarn, "psql command \"\\%s\" being ignored " % self.groups[0])
                else:
                    for i in self.line:
                        if i == "'":
                            if instring:
                                instring = 0
                            else:
                                instring = 1
                        if i == '(' and not instring:
                            bracketlevel += 1
                        if i == ')' and not instring:
                            bracketlevel -= 1
                        if not instring and bracketlevel == 0 and i == ";":
                            try:
                                curs = self.conn.cursor ()
                                curs.execute (self.cmd)
                                self.conn.commit ()
                                #gmLog.gmDefLog.Log (gmLog.lData, self.cmd)
                                curs.close ()
                            except StandardError, error:
                                if re.match (r"^NOTICE:.*", str(error)):
                                    self.log (gmLog.lWarn, error)
                                else:
                                    if self.vars['ON_ERROR_STOP']:
                                        self.log (gmLog.lErr, error)
                                        return 1
                                    else:
                                        self.log (gmLog.lData, error)
                            self.cmd = ''
                        else:
                            self.cmd += i
            self.lineno += 1
        return 0

# testing code
if __name__ == '__main__':
    from pyPgSQL import PgSQL
    conn = PgSQL.connect (host = '127.0.0.1', user='ian', database = 'tester')
    cursor = conn.cursor ()
    psql = Psql (cursor)
    import pdb
    pdb.run ('psql.run (\'/home/ian/php-drugref/sql/drugref.sql\')')# == 0:
    cursor.close ()
    conn.commit ()
    #else:
     #   conn.rollback ()
    conn.close ()
