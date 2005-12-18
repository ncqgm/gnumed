## PurePG -- DB-API 2.0 compliant postgres adaptor in pure python
## Copyright (C) 2005 Ian Haywood
## Requirements: Python >= 2.3

## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import socket, sys, struct, exceptions, types, errno, re, math, datetime

class PgTimezone (datetime.tzinfo):
    def __init__ (self, pg_tz_data="+0"):
        self.tzname = pg_tz_data
        m = re.match ("([\+\-]?[0-9]+):([0-9]+)", str(pg_tz_data))
        if m:
            self.tz = int (m.group (1))*60
            mins = int (m.group (2))
            if self.tz < 0:
                self.tz -= mins
            else:
                self.tz += mins
        else:
            self.tz = int (pg_tz_data)*60

    def utcoffset (self, dt):
        return self.tz

    def dst (self, dt):
        return datetime.timedelta (0)

    def tzname (self):
        return self.tzname

def micros (i):
    if not i:
        return 0
    i = int (i)
    l = math.floor (math.log10 (i))
    i = i * (10 ** (5-l))
    return int (i)

class Error (exceptions.StandardError):
    def __init__ (self, d):
        self.d = d
        
    def __str__ (self):
        return "%(S)s: %(M)s" % self.d
        
    def __getitem__ (self, key):
        return self.d[key]

class DatabaseError (Error):
    pass

class InterfaceError (Error):
    pass

class DataError (DatabaseError):
    pass

class OperationalError (DatabaseError):
    pass

class IntegrityError (DatabaseError):
    pass

class InternalError (DatabaseError):
    pass

class ProgrammingError (DatabaseError):
    pass

class NotSupportedError (DatabaseError):
    pass


class OperationalError (DatabaseError):
    pass

apilevel = "2.0"

threadsafety = 1
paramstyle = "format"

BINARY=1
STRING=0
NUMBER=2
DATETIME=3
ROWID=4
BOOL=5
ARRAY=6

OID_BOOL=16
OID_ARRAY_BOOL=1000
OID_INT8=20
OID_INT4=23
OID_INT2=21
OID_ARRAY_INT=1007
OID_OID=26
OID_FLOAT4=700
OID_FLOAT8=701
OID_ARRAY_FLOAT=1022
OID_DATE=1082
OID_ARRAY_DATE=1182
OID_TIMESTAMP=1114
OID_ARRAY_TIMESTAMP=1115
OID_TIME=1083
OID_ARRAY_TIME=1183
OID_TIMESTAMPTZ=1184
OID_ARRAY_TIMESTAMPTZ=1185
OID_TIMETZ=1266
OID_ARRAY_TIMETZ=1270

type_map = {OID_BOOL:BOOL, OID_INT8:NUMBER, OID_INT4:NUMBER, OID_INT2:NUMBER, OID_FLOAT4:NUMBER,
            OID_FLOAT8:NUMBER, OID_DATE:DATETIME, OID_TIMESTAMP:DATETIME, OID_TIME:DATETIME,
            OID_TIMESTAMPTZ:DATETIME, OID_TIMETZ:DATETIME,OID_ARRAY_INT:ARRAY,OID_ARRAY_FLOAT:ARRAY,OID_ARRAY_TIMESTAMP:ARRAY}


def Date(year,month,day):
    """
    This function constructs an object holding a date value.
    """
    return datetime.date (year, month, day)

def Time(hour,minute,second):
    """
    This function constructs an object holding a time value.
    """
    return datetime.time (hour,minute,second)

def Timestamp(year,month,day,hour,minute,second):
    """
    This function constructs an object holding a time stamp
    value.
    """
    return datetime.datetime (year,month,day,hour,minute,second)


def DateFromTicks(ticks):
    """
    This function constructs an object holding a date value
    from the given ticks value (number of seconds since the
    epoch; see the documentation of the standard Python time
    module for details).
    """
    return datetime.date.fromtimestamp (ticks)

def TimeFromTicks(ticks):
    """
    This function constructs an object holding a time value
    from the given ticks value (number of seconds since the
    epoch; see the documentation of the standard Python time
    module for details).
    """
    return datetime.datetime.fromtimestamp (ticks).time ()

def TimestampFromTicks(ticks):
    """
    This function constructs an object holding a time stamp
    value from the given ticks value (number of seconds since
    the epoch; see the documentation of the standard Python
    time module for details).
    """
    return datetime.fromtimestamp (ticks)
    
def Binary(string):
    """
    This function constructs an object capable of holding a
    binary (long) string value.
    """
    return string


def map_type (typ):
    if type_map.has_key (typ):
        return type_map[typ]
    else:
        return STRING

def connect (database, user, password=None, host=None, port=5432):
    """
    Connects to a database.
    
    database: the name of the database
    user: the user
    password (optional): the password
    host: the DNS name of the host to connect via TCP/IP. None for UNIX local socket connection
    port: the TCP port, default 5432
    """
    #sock = None
    err_msg = ''
    if host:
        for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                sock = socket.socket(af, socktype, proto)
            except socket.error, msg:
                sock = None
                err_msg = msg
                continue
            try:
                sock.connect(sa)
            except socket.error, msg:
                sock.close()
                err_msg = msg
                sock = None
                continue
            break
    else:
        # so we're assuming UNIX socket then
        paths = ['/tmp/.s.PGSQL.5432', '/var/run/postgresql/.s.PGSQL.5432'] # FIXME: list of paths used on various distros
        if port != 5432:
            paths.append (port)
        for path in paths:
            try:
                sock = socket.socket (socket.AF_UNIX, socket.SOCK_STREAM, 0)
                sock.connect ((path))
            except socket.error, msg:
                sock.close ()
                err_msg = msg
                sock = None
                continue
            break
    if sock is None:
        raise OperationalError ({'S':'PANIC', 'M':'Unable to connect to backend', 'C':'08001'})
    return Connection (sock, user, database, password)


sql = None

def mod_connect (database, user, password=None, host=None, port=5432):
    """
    Connect and save the connection as the module variable "sql"
    """
    global sql
    sql = connect (database, user, password=None, host=Nome, port=5432)

class Connection:
    """
    Represents a postgres connection
    """
    
    def __init__ (self, sock, user, db, password):
        self.sock = sock
        self.__password = password
        self.__user = user
        self.__input = ''
        self.__output = ''
        self.copyIn = 0
        self.numcurs = 0
        self.param = {}
        self.status = 'L'
        self.complete = 0
        self.description = []
        self.cols = []
        self.handlers = {'R':self.AuthenticationRequest, 'K':self.BackendKeyData, '2':self.BindComplete,
                         '3':self.CloseComplete, 'C':self.CommandComplete, 'I':self.EmptyQueryResponse,
                         'H':self.CopyOutResponse, 'G':self.CopyInResponse, 'c':self.CopyDone, 'n':self.NoData,
                         'd':self.CopyData, 'D': self.DataRow, 'E':self.ErrorResponse,
                         'N':self.NoticeResponse, 'A':self.NotificationResponse, 't':self.ParameterDescription,
                         'S':self.ParameterStatus, 'Z':self.ReadyForQuery, 'T':self.RowDescription,
                         '1':self.ParseComplete, 's':self.PortalSuspended}
                         
        # send login message
        self.add_struct ("!L", 196608)
        self.add_str ("user")
        self.add_str (user)
        self.add_str ("database")
        self.add_str (db)
        self.add_str ('')
        self.send ('')
        self.recv ('Z')
            
    def Error (self, error):
        """
        Handle an error
        Descendants may override this.
        By default raises a DatabaseError
        """
        self.status = 'E'
        if error['C'][0:2] == "22":
            raise DataError (error)
        if error['C'][0:2] == "23":
            raise IntegrityError (error)
        if error['C'][0:2] in ["34", "24", "25"]:
            raise InternalError (error)
        if error['C'][0:2] in ["26", "42", "3D", "3F"]:
            raise ProgrammingError (error)
        raise DatabaseError (error)

    def Notice (self, error):
        """
        An SQL NOTICE message has been recieved
        """
        pass

    def send (self, message_type):
        if message_type:
            out = struct.pack ("!cL", message_type, len (self.__output)+4)
        else:
            out = struct.pack ("!L", len (self.__output) + 4)
        out += self.__output
        self.__output = ""
        try:
            ret = self.sock.sendall (out)
        except socket.error, msg:
            if type (msg) == types.TupleType:
                err, msg = msg
            self.Error ({'S':'PANIC', 'M':msg, 'C':'08006'})
        return ret

    def recv (self, terminators):
        """
        This is where we listen for a packets.
        """
        while 1:
            try:
                self.__input += self.sock.recv (10000)
                processing = 1
                while processing:
                    if len (self.__input) > 4:
                        message_type, msg_len = struct.unpack ("!cL", self.__input[0:5])
                        if len (self.__input) >= msg_len + 1:
                            excess = self.__input[msg_len+1:]
                            self.__input = self.__input[5:msg_len+1]
                            if self.handlers.has_key (message_type):
                                self.handlers[message_type] ()
                                self.__input = excess
                                #print self.handlers[message_type].__name__
                                if message_type in terminators:
                                    return
                            else:
                                self.Error ({'S':'PANIC', 'M':'unknown packet %s' % message_type, 'C':'08006'})
                        else:
                            processing = 0
                    else:
                        processing = 0
            except socket.error, msg:
                if type (msg) == types.TupleType:
                    err, msg = msg
                self.Error ({'S':'PANIC', 'M':msg, 'C':'08006'})

            
    def add_struct (self, fmt, *args):
        self.__output += struct.pack (fmt, *args)

    def get_struct (self, fmt):
        length = struct.calcsize (fmt)
        if length > len (self.__input):
            return None
        ret = struct.unpack (fmt, self.__input[0:length])
        if len (ret) == 1:
            ret, = ret
        self.__input = self.__input[length:]
        return ret

    def add_str (self, string):
        self.__output += string
        self.__output += '\000'

    def add_raw (self, string):
        self.__output += string

    def get_str (self):
        strend = 0
        while strend < len (self.__input) and self.__input[strend] != '\000':
            strend += 1
        if strend == 0:
            return ""
        else:
            ret = self.__input[0:strend]
            self.__input = self.__input[strend+1:]
            return ret

    def get_raw (self, length):
        ret = self.__input[0:length]
        self.__input = self.__input[length:]
        return ret

    def reset (self):
        self.rows = []
        self.rowcount = -1
            
                
    def AuthenticationRequest (self):
        mode = self.get_struct ("!L")
        if mode == 0:
            self.__loggedin = 1
            self.__status = ''
        elif mode == 1:
            self.Error ({'S':'PANIC', 'C':'08004', 'M':'Kerberos V4 authentication not supported', 'H':'You need to remove this option from pg_hba.conf'})
        elif mode == 2:
            self.Error ({'S':'PANIC', 'C':'08004', 'M':'Kerberos V5 authentication not supported', 'H':'You need to remove this option from pg_hba.conf'})
        elif mode == 3: # clear text password
            self.add_str (self.__password)
            self.send ('p')
        elif mode == 4: # crypt () password
            salt = self.get_struct ("2s")
            import crypt
            self.add_str (crypt.crypt (self.__password, salt))
            self.send('p')
        elif mode == 5: # md5 password
            salt = self.get_struct ("4s")
            import md5
            md5_1 = md5.new (self.__password + self.__user)
            md5_2 = md5.new (md5_1.hexdigest () + salt)
            self.add_str ("md5" + md5_2.hexdigest ())
            self.send('p')
        elif mode == 6:
            self.Error({'S':'PANIC', 'C':'08004', 'M':'SCM authentication not supported', 'H':'You need to remove this option from pg_hba.conf'})
        else:
            self.Error ({'S':'PANIC', 'C':'08004', 'M':'Unknown authentication mode %d' % mode, 'H':"You're screwed"})

    def BackendKeyData (self):
        self.backend_pid, self.backend_key = self.get_struct ("!LL")

    def CommandComplete (self):
        complete = self.get_str ()
        res = ['INSERT [0-9]+ ([0-9]+)', 'FETCH ([0-9]+)', 'DELETE ([0-9]+)', 'MOVE ([0-9]+)', 'UPDATE ([0-9]+)']
        self.complete = 1
        for r in res:
            match = re.match (r, complete)
            if match:
                self.rowcount = int (match.group (1))
                return
        self.rowcount = 0
        

    def CopyData (self):
        data = self.get_raw (self.msg_len-4)
        self.queryqueue[0].callback (data)

    def CopyDone (self):
        self.rowcount = 0

    def CopyOutResponse (self):
        overall, num_cols = self.get_struct ("!BH")
        cols = self.get_struct("%dH" % num_cols)
        self.description = [('', c, None, None, None, None, None) for c in cols] 

    def CopyInResponse (self):
        self.copyIn = 1
        overall, num_cols = self.get_struct ("!BH")
        cols = self.get_struct("%dH" % num_cols)
        self.description = [('', c, None, None, None, None, None) for c in cols] 


    def BindComplete (self):
        pass

    def EmptyQueryResponse (self):
        self.rowcount = 0

    def CloseComplete (self):
        pass

    def NoData (self):
        self.description = None

    def ParseComplete (self):
        pass

    def PortalSuspended (self):
        self.finished = 1

    def parse (self, typ, data):
        if data[0] == '{' and data[-1] == '}':
            # it's an array
            # FIXME: better way of detecting arrays?
            ret = []
            mode = 0
            x = ''
            for i in data[1:-1]:
                if mode == 0: # what's next? mode
                    if i == "'":
                        mode = 1
                    elif i == "{":
                        mode = 2
                        x += i
                    elif i == '"':
                        mode = 5
                    else:
                        mode = 3
                        x += i
                elif mode == 1: # string mode
                    if i == "\\":
                        mode = 4
                    elif i == "'":
                        mode = 3
                    else:
                        x += i
                elif mode == 2: # sub-array mode
                    if i == "}":
                        x += i
                        mode = 3
                    else:
                        x += i
                elif mode == 3: # number/waiting-for-comma mode
                    if i == ",":
                        mode = 0
                        ret.append (x)
                        x = ''
                    elif i == "'":
                        x += i
                        mode = 1
                    else:
                        x += i
                elif mode == 4: # escape char in string mode
                    if i == "n":
                        x += "\n"
                    elif i == "'":
                        x += "'"
                    elif i == "r":
                        x += "\r"
                    elif i == "\\":
                        x += i
                elif mode == 5: # date-in-array mode
                    if i == '"':
                        mode = 3
                    else:
                        x += i
            ret.append (x)
            return [self.parse (typ, i) for i in ret]                
        else:
             if typ in [OID_INT2, OID_INT4, OID_OID, OID_INT8, OID_ARRAY_INT]:
                 return int (data)
             elif typ in [OID_BOOL,OID_ARRAY_BOOL]:
                 return data == 't'
             elif typ in [OID_FLOAT4,OID_FLOAT8,OID_ARRAY_FLOAT]:
                 return float (data)
             elif typ in [OID_DATE,OID_ARRAY_DATE]:
                 m = re.match ('(\d+)-(\d+)-(\d+)', data)
                 if m is None:
                     raise InterfaceError, "unable to parse '%s', which the backend told us was a date" % data
                 return datetime.date (int (m.group(1)), int (m.group(2)), int (m.group (3)))
             elif typ in [OID_TIMESTAMP,OID_TIMESTAMPTZ,OID_ARRAY_TIMESTAMP,OID_ARRAY_TIMESTAMPTZ]:
                 m = re.match ('(\d+)-(\d+)-(\d+) (\d+)\:(\d+)\:?([0-9]*)\.?([0-9]*)([\+-]?[0-9\.]*)', data)
                 if m is None:
                     raise InterfaceError, "unable to parse '%s', which the backend told us was a timestamp" % data
                 return datetime.datetime (int (m.group (1)), int (m.group (2)), int (m.group (3)), int (m.group (4)), int (m.group (5)), (m.group (6) and int (m.group (6))) or 0, micros (m.group (7)), (m.group (8) and PgTimezone (m.group (8))) or None)
             elif typ in [OID_TIME,OID_ARRAY_TIME,OID_TIMETZ,OID_ARRAY_TIMETZ]:
                 m = re.match ('(\d+)\:(\d+)\:?([0-9]*)\.?([0-9]*)([\+-]?[0-9\.]*)', data)
                 if m is None:
                     raise InterfaceError, "unable to parse '%s', which the backend told us was a time" % data
                 return datetime.time (int (m.group (1)), int (m.group (2)), (m.group (3) and int (m.group (3))) or 0, micros (m.group (4)), (m.group (5) and PgTimezone (m.group (5))) or None)  
             else:
                 # print "Unknown type %d, data %s" % (typ, data)
                 return data

    def DataRow (self):
        cols = self.get_struct ("!h")
        row = []
        for i in range (0, cols):
            itemlen = self.get_struct ("!l")
            typ = self.cols[i]['typeOID']
            format = self.cols[i]['format']
            if itemlen == -1:
                row.append (None) # map SQL NULL to Python None
            elif format == 1:
                if typ == OID_INT2:
                    row.append (self.get_struct ("!h"))
                elif typ in [OID_INT4, OID_OID]:
                    row.append (self.get_struct ("!l"))
                elif typ == OID_INT8:
                    row.append (self.get_struct ("!q"))
                elif typ == OID_BOOL:
                    row.append (self.get_struct ("c") == 0)
                elif typ == OID_FLOAT4:
                    row.append (self.get_struct ("f"))
                elif typ == OID_FLOAT8:
                    row.append (self.get_struct ("d"))
                else:
                   self.Error ({'S':'PANIC', 'M':'Unknown binary format', 'D':'The server has tried to send us (the purepg module) an object of type OID %d in type 1 (binary) format, which we do not understand' % typ, 'C':'XX000'})
            elif format == 0: # text format
                row.append (self.parse (typ, self.get_raw (itemlen)))
            else:
                self.Error ({'S':'PANIC', 'M':'Unknown format code %d' % format, 'D':'The server tried to send us some data in an unknown data format', 'C':'XX000'})
        self.rows.append (row)

    def ErrorResponse (self):
        fieldtype, = self.get_struct ("c")
        error = {}
        while fieldtype != '\000':
            error[fieldtype] = self.get_str ()
            fieldtype, = self.get_struct ("c")
        self.__status = 'E'
        self.copyIn = 0
        self.Error (error)
        self.complete = 1

    def NoticeResponse (self):
        fieldtype = self.get_struct ("c")
        error = {}
        while fieldtype != '\000':
            error[fieldtype] = self.get_str ()
            fieldtype = self.get_struct ("c")
        self.Notice (error)
        
    def NotificationResponse (self):
        pid = self.get_struct ("!L")
        event = self.get_str ()
        param = self.get_str ()
        if self.__listeners.has_key (event):
            self.__listeners[event] (pid, param)

    def Listen (self, event, callback):
        """
        EXTENSION:
        Listens for a  notification event
        @type callback: callable
        @param callback: the function called, must accept two parameters:
               1. the process ID of the backend raising this event
               2. the notification parameter (not yet supported)
        Should be None to cancel
        Note this won't issue the backend LISTEN command for you!
        """
        if callback is None:
            del self.__listeners[event]
        else:
            if not callable (callback):
                raise InterfaceError, "notification callback must be callable"
            self.__listeners[event] = callback

    def ParameterDescription (self):
        pass

    def ParameterStatus (self):
        p = self.get_str ()
        self.param[p] = self.get_str ()

    def ReadyForQuery (self):
        self.status = self.get_struct ("c")
    

    def RowDescription (self):
        cols = self.get_struct ("!h")
        self.cols = []
        self.description = []
        for i in range (0, cols):
            col = {}
            col['name'] = self.get_str ()
            col['tableOID'], col['col_no'], col['typeOID'], col['typlen'], col['modifier'], col['format'] = self.get_struct ("!lhlhlh")
            self.cols.append (col)
        self.description = [(i['name'], map_type (i['typeOID']), None, i['typlen'], None, None, None) for i in self.cols]

    def close (self):
        self.send ('X')
        self.sock.close ()

    def parse_quotes (self, arg):
        if type (arg) == types.ListType or type (arg) == types.TupleType:
            s = "{%s}" % ",".join ([self.parse_array (i) for i in arg])
            return "'%s'" % s.replace ("'", "''")
        elif type (arg) == types.BooleanType:
            if arg:
                return "'t'"
            else:
                return "'f'"
        elif isinstance (arg, types.StringTypes):
            arg = arg.replace ("'", "''")
            arg = arg.replace ("\\", "\\\\")
            if type (arg) == types.UnicodeType:
                arg = arg.encode ('utf-8', 'replace')
            return "'%s'" % arg
        elif isinstance (arg, (datetime.date, datetime.time, datetime.datetime)):
            return "'%s'" % arg.isoformat ()
        elif arg is None:
            return 'NULL'
        else:
            # try our best!
            return str (arg)

    def parse_array (self, arg):
        if type (arg) == types.ListType or type (arg) == types.TupleType:
            s = "{%s}" % ",".join ([self.parse_array (i) for i in arg])
            return "'%s'" % s.replace ("'", "''")
        elif type (arg) == types.BooleanType:
            if arg:
                return "t"
            else:
                return "f"
        elif isinstance (arg, types.StringTypes):
            arg = arg.replace ("'", "''")
            arg = arg.replace ("\\", "\\\\")
            if type (arg) == types.UnicodeType:
                arg = arg.encode ('utf-8', 'replace')
            return "'%s'" % arg
        elif isinstance (arg, (datetime.date, datetime.time, datetime.datetime)):
            return "'%s'" % arg.isoformat ()
        elif arg is None:
            return 'NULL'
        else:
            # try our best!
            return str (arg)


    def parse_noquotes (self, arg):
        if type (arg) == types.ListType or type (arg) == types.TupleType:
            return "{%s}" % ",".join ([self.parse_array (i) for i in arg])
        elif type (arg) == types.BooleanType:
            if arg:
                return "t"
            else:
                return "f"
        elif isinstance (arg, types.StringTypes):
            if type (arg) == types.UnicodeType:
                arg = arg.encode ('utf-8', 'replace')
            return arg
        elif isinstance (arg, (datetime.date, datetime.time, datetime.datetime)):
            return arg.isoformat ()
        elif arg is None:
            return 'NULL'
        else:
            # try our best!
            return self.parse_noquotes (str (arg))

    def commit (self):
        if self.status == 'X':
            self.reset ()
            self.send ("S") # Sync
            self.recv ('Z') # wait for ReadyForQuery
        if self.status == 'I':
            return
        if self.status == 'E':
            raise DatabaseError, "in error mode, can't commit"
        if self.status == 'Q':
            self.recv ('Z')
        if self.status == 'T':
            self.add_str ("COMMIT")
            self.send ("Q")
            self.recv ('Z')

    def rollback (self):
        if self.status == 'X':
            self.reset ()
            self.send ("S") # Sync
            self.recv ('Z') # wait for ReadyForQuery
        if self.status == 'I':
            raise DatabaseError, "no transaction to roll back"
        if self.status == 'Q':
            self.recv ('Z')
        if self.status == 'T' or self.status == 'E':
            self.add_str ("ROLLBACK")
            self.send ("Q")
            self.recv ('Z')

    def query (self, query, *args):
        """
        EXTENSION: for cursor-less queries
        accepts and query string and args as for cursor.execute ()
        Immediately executes the query and returns the string
        NOTE: this will close all open cursors
        However, it is slightly faster
        """
        if self.status == 'X':
            self.reset ()
            self.send ("S") # Sync
            self.recv ('Z') # wait for ReadyForQuery
        if args:
            args = [self.parse_quotes (i) for i in args]
            query = query % tuple (args)
        self.add_str (query)
        self.send ('Q')
        self.status = 'Q'
        self.reset ()
        self.recv ('Z')
        self.rowcount = len (self.rows)
        return self.rows

    def socket (self):
        """
        EXTENSION:
        returns the underlying socket object, for use in select () etc.
        Handle with care!
        """
        return self.sock

    def cursor (self, name=None):
        return Cursor (self)


    def __getattr__ (self, attr):
        """
        EXTENSION:
        Allows the user to call prepared queries as methods of this class
        """
        func = PreparedQuery (self, attr)
        self.__dict__[attr] = func
        return func 
        

    def pquery (self, query, *args):
        if self.__dict__.has_key (query):
            func = self.__dict__[query]
        else:
            func = PreparedQuery (self, query)
            self.__dict__[query] = func
        return func (*args)

    def insert (self, table, pk_name, values):
        """
        A convience method for inserting rows
        returns a PgRow instance
        values is a dict of values keyed by field namem without the pk
        returns the new pk
        expects the sequence counter is called 'table_pk_seq'
        """
        r = self.query ("begin; insert into %s (%s) values (%s); select curr_val ('%s_%s_seq'); commit" % (table, ','.join (values.keys ()), ','.join ([self.parse_quotes (i) for i in values.values ()]),pk_name))
        return r[0][0]
                        
        

class Cursor:
    def __init__ (self, conn):
        self.conn = conn
        self.arraysize = 10
        self.description = None

    def close (self):
        pass # doesn't really mean anything in this implemetation

    def __nextdollar (self, match):
        self.n += 1
        return "$%d" % self.n
    

    def __makedollars (self, query):
        # replace %s with $1, $2, etc.
        self.n = 0
        return re.sub ("%s", self.__nextdollar, query)


    def execute (self, query, *args):
        self.conn.numcurs += 1
        self.name = 'p%d' % self.conn.numcurs
        query = self.__makedollars (query)
        self.conn.status = 'X' # eXtended query mode
        self.conn.add_str (self.name)
        self.conn.add_str (query)
        self.conn.add_struct ("!H", 0)
        self.conn.send ("P")
        self.conn.add_str (self.name)
        self.conn.add_str (self.name)
        self.conn.add_struct ("!HHH", 1, 0, len (args))
        for i in args:
            if i is None:
                self.conn.add_struct ("!i", -1)
            else:
                s = self.conn.parse_noquotes (i)
                self.conn.add_struct ("!i", len (s))
                self.conn.add_raw (s)
        self.conn.add_struct ("!HH", 1, 0)
        self.conn.send ('B')
        self.conn.add_str ("P%s" % self.name)
        self.conn.send ("D")
        self.conn.send("H")
        self.conn.reset ()
        self.conn.description = None
        self.conn.recv ('nT')
        self.description = self.conn.description
        self.cols = self.conn.cols
        if self.description is None:
            self.conn.add_str (self.name)
            self.conn.add_struct ("!i", 0)
            self.conn.send  ("E")
            self.conn.send ("H")
            self.conn.reset ()
            self.conn.recv ('CI')
        
    def executemany (self, query, list_of_args):
        """
        WARNING: all results are discarded
        """
        self.conn.status = 'X'
        query = self.__makedollars (query)
        self.conn.add_str ('')
        self.conn.add_str (query)
        self.conn.add_struct ("!H", 0)
        self.conn.send ("P")
        for args in list_of_args:
            self.conn.add_str ('')
            self.conn.add_str ('')
            self.conn.add_struct ("!HHH", 1, 0, len (args))
            for i in args:
                if i is None:
                    self.conn.add_struct ("!i", -1)
                else:
                    s = self.conn.parse_noquotes (i)
                self.conn.add_struct ("!i", len (s))
                self.conn.add_raw (s)
            self.conn.add_struct ("!HH", 1, 0)
            self.conn.send ('B')
            self.conn.add_str ("P")
            self.conn.send ("D")
            self.conn.reset ()
            self.conn.add_str ('')
            self.conn.add_struct ("!i", 0)
            self.conn.send  ("E")
            self.conn.send("H")
            self.conn.recv ('CI')

    def fetchone (self):
        ret = self.fetchmany (1)
        if not ret:
            return None
        else:
            return ret[0]

    def fetchmany (self, size=-1):
        if size == -1:
            size = self.arraysize
        self.conn.add_str (self.name)
        self.conn.add_struct ("!i", size)
        self.conn.send ("E")
        self.conn.send ("H")
        self.conn.reset ()
        self.conn.complete = 0
        self.conn.cols = self.cols # restore column types for parsing
        self.conn.recv ('CIs')
        self.rowcount = len (self.conn.rows)
        r = self.conn.rows
        if self.conn.complete:
            self.conn.add_str ("P%s" % self.name)
            self.conn.send ("C")
            self.conn.send ("H")
            self.conn.reset ()
            self.conn.recv ('3')
        return r

    def fetchall (self):
        return self.fetchmany (0)

    def setinputsizes (size):
        pass

    def setoutputsize (size):
        pass

    def nextset (self):
        raise NotSupportedError, "not implemented"

    def callproc (procname, *args):
        raise NotSupportedError, "not implemented"


class PreparedQuery:
    """
    Represents a prepared query on the backend.
    They are accessed by calling the Connection object as
    if there were a method with the name of the prepared query
    (you must issue the PREPARE..AS command first.)
    The parameters are those of the query.
    The result is a list of dictionaries, keyed by the column name.

    This object can also act as a list, representing rows of a linked
    table from a PgRow row. 9see PgRow)
    """
    
    def __init__ (self, conn, query, master=None):
        self.query = query
        self.conn = conn
        self.cols = None
        q = query.split ("_")
        self.table = q[-1] # table name is the last underscore-separated word
        self.master = master
        self.list = None
        self.to_delete = []
        self.to_add = []
        if PgRowSubclasses.has_key (self.table):
            self.klass = PgRowSubclasses[self.table]
        else:
            self.klass = PgRow
        if "%s" in self.klass.fk_name:
            aelf.pk_master_name = self.klass.fk_name % self.master.table
        else:
            self.pk_master_name = self.klass.fk_name
  
        
    def __call__ (self, *args):
        self.conn.status = 'X' # eXtended query mode
        self.conn.add_str (self.query)
        self.conn.add_str (self.query)
        if not self.master is None:
            args[0:0] = [self.master.get_pk ()]
        self.conn.add_struct ("!HHH", 1, 0, len (args))
        for i in args:
            if i is None:
                self.conn.add_struct ("!i", -1)
            else:
                s = self.conn.parse_noquotes (i)
                self.conn.add_struct ("!i", len (s))
                self.conn.add_raw (s)
        self.conn.add_struct ("!HH", 1, 0)
        self.conn.send ('B')
        if not self.cols:
            self.conn.add_str ("P%s" % self.query)
            self.conn.send ("D")
            self.conn.reset ()
            self.conn.description = None
        else:
            self.conn.cols = self.cols
        # now fetch the data
        self.conn.add_str (self.query)
        self.conn.add_struct ("!i", 0)
        self.conn.send ("E")
        self.conn.reset ()
        self.conn.complete = 0
        self.conn.add_str ("P%s" % self.query)
        self.conn.send ("C")
        self.conn.send ("H")
        self.conn.recv ('3')
        self.cols = self.conn.cols
        return [self.klass (self.conn, self.table, cols=self.cols, data=i) for i in self.conn.rows]

    def __len__ (self):
        if self.list is None:
            self.__get_list ()
        return len (self.list)

    def __getitem__ (self, key):
        if self.list is None:
            self.__get_list ()
        return self.list[key]

    def refresh (self):
        self.__get_list ()

    def __delitem__ (self, n):
        """
        delete a row, this is deferred until .save ()
        """
        if self.list is None:
            self.__get_list ()
        self.to_delete.append (self.list[n])
        del self.list[n]

    def new (self, pk_master_name=None, **kwargs):
        """
        Add a row to the table
        kwargs: the fields of the new row
        pk_master_name: the name of the field holding the primary key of our ancestor table
        (i.e the foreign key)
        defaults to fk_master where master is the name of the master table.
        primary key of the table must be "pk"
        deferred until .save ()
        """
        if self.master is None:
            raise OperationalError ({'S':'ERROR', 'M':'Object cannot be a list', 'C':'00000'})
        if pk_master_name is None:
            pk_master_name = self.pk_master_name
        kwargs[pk_master_name] = self.master.get_pk ()
        kwargs[klass.pk_name] = None
        r = klass (self.conn, self.table, data_dict=kwargs)
        if self.list:
            self.list.append (r)
        return r
        

    def __get_list (self):
        """
        We are being used as a list, run the get_XXX prepared query to
        act as a list
        """
        if self.master is None:
            raise OperationalError ({'S':'ERROR', 'M':'Object cannot be a list', 'C':'00000'})
        l = self.conn.query ("select * from %s where %s = %%s" % (self.table, self.pk_master_name), self.master.get_pk ())
        self.list = [self.klass (self.conn, self.table, data=i, cols=self.conn.cols) for i in l]
        
    def save (self):
        """
        actually delete deleted rows, and call .update () on all the others
        """
        if self.list is None:
            return
        for i in self.to_delete:
            i.delete ()
        self.to_delete = []
        for i in self.list:
            i.update ()


PgRowSubclasses = {} # a dictionary of known subclasses of PgRow, keyed by table name

class PgRow:
    """
    Represents a row on the backend database, fields can be access by name
    as attributes, or like a list by field number.
    
    If an attribute does not exist, it will make a prepared query object with that name.
    This object can be used in two ways
    1/ it can be called as a method, in this case a prepared query of the same
    name must exist on the backend, the primary key of this row (must be called "pk") is passed as the
    first parameter (so the query is like an SQL  'method' on the row 'object'
    2/ the can be used as a list. in this case, it's expected a table exists of the
    same name, and this table has one primary key called "pk"
    get_XXX must accept one parameter, being the primary key of this row, also called "pk", and returns the linked
    rows of the table.
    The backend tables and fields do not have to match these naming rules if you don't want to use the list
    features, you can just use it as a plain data row.

    PgRow can be subclassed, subclasses should be registered in the module variable PgRowSubclasses
    """

    pk_name = 'pk'
    fk_name = 'fk_%s'
    
    def __init__ (self, conn, table, cols=None, data=None, data_dict=None):
        if data_dict:
            self.data = data_dict
        else:
            self.data = dict ([(cols[j]['name'],i[j]) for j in range (0, len (cols))])
        self.table = table
        self.cols = cols
        self.conn = conn
        self.dirty = []
        
    def __getattr__ (self, key):
        if self.data.has_key (key):
            return self.data[key]
        else:
            if self.get_pk () is None:
                raise OperationalError ({'S':'ERROR', 'M':'Table row has not yet been created', 'C':'00000'})
            d = PreparedQuery (self.conn, key, master=self)
            self.data[key] = d
            return d

    def __setattr__ (self, key, val):
        if not self.data.has_key (key) or val != self.data[key]:
            if not key in self.dirty:
                self.dirty.append (key)
            self.data[key] = val

    def __getitem__ ( self, key):
        # will fail if we are a freshly created row 9as our items have no instrinsic order
        return self.data[self.cols[key]['name']]
    
    def update ():
        """
        updates changes to be backend table.
        the query table must end with an underscore and the table name for this to work
        the primary key must exist and be called "pk"
        so "find_patient" for table "patient" etc.
        also saves data for any linked tables that where accessed via this object
        """
        if self.get_pk () is None:
            del self.data[self.__class__.pk_name]
            self.data[self.__class__.pk_name] = self.conn.insert (self.table, self.__class__.pk_name, self.data)
            self.dirty = []
        else:
            if self.dirty:
                s = ','.join (['%s=%s' % (i, self.conn.parse_quotes (self.data[i])) for i in self.dirty])
                s = 'update %s set %s where %s=%s' % (self.table, s, self.__class__.pk_name, self.get_pk ())
                self.conn.query (s)
                self.dirty = []
                if self.conn.rowcount == 0:
                    raise OperationalError ({'S':'ERROR', 'M':'Database  record no longer exists', 'C':'00000'})
            for i in self.data.values ():
                if isinstance (i, PreparedQuery):
                    i.save ()
            

    def delete ():
        """
        deletes the table
        the query name must end in an underscore and the table name
        the primary key must ecist and be called "pk"
        """
        if self.data[self.__class__.pk_name] is None:
            return # we don't really exist anyway
        self.conn.query ('delete from %s where pk=%s', self.table, self.get_pk ())
            
    def get_pk (self):
        return self.data[self.__class__.pk_name]
        
if __name__ == '__main__':
    print "purepg"
    print "Copyright (C) 2005 Ian Haywood"
    import os, getpass
    if len (sys.argv) < 2:
        print """
Unit-testing script
We need a postgres server which a database on which we can create tables
Arguments: database [user [host]]"""
        sys.exit (0)
    if len (sys.argv) > 3:
        host = sys.argv[3]
    else:
        host = None
    if len (sys.argv) > 2:
        user = sys.argv[2]
    else:
        user = getpass.getuser ()
    database = sys.argv[1]
    password = getpass.getpass ()
    pg = connect (database, user, password, host)
    pg.query ("create table test (a1 text, a2 integer)")
    pg.query ("create table test2 (a1 boolean [], a2 time [], a3 date [], a4 timetz [], a5 timestamptz [])")
    pg.query ("begin work")
    cur = pg.cursor ()
    cur.executemany ("insert into test values (%s, %s)", [["foo", 3], ['bar', 4]])
    cur.execute ("insert into test values (%s, %s)", "baz", 7)
    pg.commit ()
    pg.query ("insert into test2 values (%s, %s, %s, %s, %s)", [True, False], [datetime.time (4, 34, 23)], [datetime.date.today ()], [datetime.time(7, 14, 13)], [datetime.datetime.now (), datetime.datetime.utcnow ()]) 
    cur = pg.cursor ()
    cur.execute ("select * from test")
    cur2 = pg.cursor ()
    cur2.execute ("select * from test2")
    print cur.fetchall ()
    print cur2.fetchall ()
    pg.query ("prepare xyz (integer) as select * from test where a2=$1")
    print pg.xyz (7)
    pg.query ("drop table test")
    pg.query ("drop table test2")
    pg.close ()
    
        
            
    
