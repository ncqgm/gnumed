#!/bin/sh -
# popserve2.py by H. Suzuki <suzuki@acm.org>
"exec" "python" "-O" "$0" "$@"
__doc__ = """Simple POP3 Server 2 (7 March 2003)

This is a simple POP3 server written in Python.  It has backends to
read mails in RMAIL or mbox; thus it allows you to read Unix mails
from anywhere via POP3.

It runs on Python 2.2.*, Python 2.1.* and Jython 2.1.

The main class is PopServer; it constructs and uses Maildrop and Session
objects internally.  See RFC1939 for POP3.  This program is derived from
http://www.garshol.priv.no/download/software/python/popserve.py

I would ask that you refer to this program and the original popserve.py
when you make use of or incorporate this program into another product.
Bug reports and patches are welcome.
"""

import socket, md5, traceback

class Error (Exception): pass

class Maildrop:
    def __init__(self, msg_list):
        self.__mails = [(0, msg) for msg in msg_list]

    def update(self, server):
        self.__mails = [(0, msg) for (deleted, msg) in self.__mails
                        if not deleted]
        # XXX (it does not update the orignal msg_list on the server)

    def get_stat(self):
        num = sum = 0
        for (deleted, msg) in self.__mails:
            if not deleted:
                num += 1
                sum += len(msg)
        return num, sum

    def __getitem__(self, i):
        try:
            return self.__mails[i]
        except IndexError:
            raise Error, "No such message"

    def get_list(self, func):
        result = []
        for i in range(len(self.__mails)):
            (deleted, msg) = self.__mails[i]
            if not deleted:
                result.append((i, func(msg)))
        return result

    def get_msg(self, i):
        (deleted, msg) = self[i]
        if deleted:
            raise Error, "Message has been deleted"
        return msg

    def delete_msg(self, i):
        (deleted, msg) = self[i]
        if deleted:
            raise Error, "Message already deleted"
        self.__mails[i] = (1, msg)

    def reset(self):
        for i in range(len(self.__mails)):
            (deleted, msg) = self.__mails[i]
            if deleted:
                self.__mails[i] = (0, msg)

class PopServer:
    COMMANDS = ("QUIT", "STAT", "LIST", "RETR", "DELE", "NOOP", "RSET",
                "TOP", "UIDL", "USER", "PASS")

    def __init__(self, check_user, check_passwd, get_mails_for):
        self.check_user = check_user
        self.check_passwd = check_passwd
        self.__get_mails_for = get_mails_for
        self.__drops = {}

    def get_maildrop(self, username):
        drop = self.__drops.get(username)
        if drop is None:
            mails = self.__get_mails_for(username)
            drop = Maildrop(mails)
            self.__drops[username] = drop
        else:
            drop.reset()
        return drop

    def main_loop(self, port=110):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', port))
        s.listen(1)
        print "Serving POP3 on port", port
        while 1:
            conn, addr = s.accept()
            print "Connected with:", addr
            self.session(conn)

    def session(self, conn):
        "(self, socket_obj) -> None"
        wf = conn.makefile('wb')
        session = Session(wf, self)
        session.write_ok("POP3 server ready")
        wf.flush()
        while 1:
            try:
                line = conn.recv(2048)
                if not line:
                    print "(disconnected)"
                    wf.close()
                    conn.close()
                    break
                print line[:-1]
                comm = line.split()
                if not comm:
                    continue
                (cmd, args) = (comm[0].upper(), comm[1:])
                if cmd not in self.COMMANDS:
                    raise Error, "Unknown command"
                method = getattr(session, cmd, None)
                if method is None:
                    raise Error, "Unsupported command"
                method(*args)
            except (TypeError, Error), msg:
                print "-ERR", msg
                wf.write("-ERR %s\r\n" % msg)
                if not isinstance(msg, Error):
                    traceback.print_exc()
            wf.flush()
            if cmd == "QUIT":
                wf.close()
                conn.close()
                break

class Session:
    # states
    Q_AUTHORIZATION_USER = "AUTHORIZATION (USER)"
    Q_AUTHORIZATION_PASS = "AUTHORIZATION (PASS)"
    Q_TRANSACTION = "TRANSACTION"

    def __init__(self, wf, server):
        self.server = server
        self.write = wf.write
        self.state = Session.Q_AUTHORIZATION_USER
        self.username = None
        self.maildrop = None

    def write_ok(self, msg):            # sends an OK response.
        print "+OK " + msg
        self.write("+OK %s\r\n" % msg)

    def write_multi(self, lines):       # write "byte-stuffed" lines.
        for s in lines:
            if s[:1] == ".":            # termination octet?
                s = "." + s
            self.write(s + "\r\n")

    def __check_state(self, STATE):
        if self.state is not STATE:
            raise Error, "Wrong state " + self.state

    def QUIT(self):
        if self.state is Session.Q_TRANSACTION:
            self.maildrop.update(self.server)
        self.write_ok("Good bye...")

    def USER(self, username):
        #self.__check_state(Session.Q_AUTHORIZATION_USER)
        #if not self.server.check_user(username):
        #   raise Error, "Unknown user %s" % username
        self.username = username
        self.state = Session.Q_AUTHORIZATION_PASS
        self.write_ok("User %s accepted" % username)

    def PASS(self, password):
        #self.__check_state(Session.Q_AUTHORIZATION_PASS)
        #if not self.server.check_passwd(self.username, password):
        #    raise Error, "Invalid password"
        self.maildrop = self.server.get_maildrop(self.username)
        self.state = Session.Q_TRANSACTION
        self.write_ok("Password accepted")

    def STAT(self):
    	print "up to here"
        self.__check_state(Session.Q_TRANSACTION)
        self.write_ok("%d %d" % self.maildrop.get_stat())

    def LIST(self, msgno=None):
        self.__check_state(Session.Q_TRANSACTION)
        if msgno is None:
            self.write_ok("scan listing begins")
            for (no, size) in self.maildrop.get_list(len):
                line = "%d %d" % (no + 1, size)
                self.write(line + "\r\n")
                print line
            self.write(".\r\n")
        else:
            msg = self.maildrop.get_msg(_get_no(msgno))
            self.write_ok("%s %d" % (msgno, len(msg)))

    def RETR(self, msgno):
        self.__check_state(Session.Q_TRANSACTION)
        msg = self.maildrop.get_msg(_get_no(msgno))
        lines = msg.split("\r\n")
        self.write_ok("Sending message")
        self.write_multi(lines)
        self.write(".\r\n")

    def DELE(self, msgno):
        self.__check_state(Session.Q_TRANSACTION)
        self.maildrop.delete_msg(_get_no(msgno))
        self.write_ok("Message deleted")

    def NOOP(self):
        self.__check_state(Session.Q_TRANSACTION)
        self.write_ok("Still here...")

    def RSET(self):
        self.__check_state(Session.Q_TRANSACTION)
        self.maildrop.reset()
        self.write_ok("Messages unmarked")

    def TOP(self, msgno, n):
        self.__check_state(Session.Q_TRANSACTION)
        try:
            n = int(n)
        except ValueError:
            raise Error, "Not a number"
        msg = self.maildrop.get_msg(_get_no(msgno))
        [head, body] = msg.split("\r\n\r\n", 1)
        self.write_ok("Top of message follows")
        self.write_multi(head.split("\r\n"))
        self.write("\r\n")
        self.write_multi(body.split("\r\n")[:n])
        self.write(".\r\n")

    def UIDL(self, msgno=None):
        self.__check_state(Session.Q_TRANSACTION)
        if msgno is None:
            self.write_ok("UIDL listing begins")            
            for (no, uid) in self.maildrop.get_list(_digest):
                line = "%d %s" % (no + 1, uid)
                self.write(line + "\r\n")
                print line
            self.write(".\r\n")
        else:
            msg = self.maildrop.get_msg(_get_no(msgno))
            self.write_ok("%s %s" % (msgno, _digest(msg)))

def _digest(msg):
    i = msg.find("\r\nMessage-")
    if i >= 0:
        if msg[i+10: i+14].upper() == "ID: ":
            j = msg.find("\r\n", i+14)
            if j >= 0:
                msgid = msg[i+14: j]
                if len(msgid) > 10:
                    return md5.new(msgid).hexdigest()
    return md5.new(msg).hexdigest()

def _get_no(msgno):
    try:
        return int(msgno) - 1
    except ValueError:
        raise Error, "Not a number"

def read_mbox(file_name):
    "A backend to read mails from an mbox file"
    f = open(file_name)
    result = []
    current = []
    while 1:
        line = f.readline()
        if not line or (line[:5] == "From " and
                        (not current or current[-1:] == [""])):
            if current:
                if current[-1:] == [""]:
                    current = current[:-1]
                msg = "\r\n".join(current)
                result.append(msg)
                del current[:]
            if not line:
                break
        else:
            current.append(line[:-1])
    f.close()
    return result

def read_RMAIL(file_name):
    "A backend to read mails from an RMAIL file of Emacs"
    f = open(file_name)
    result = []
    inheader = 1
    current = []
    while 1:
        line = f.readline()
        if not line:
            break
        elif inheader:
            if line == "*** EOOH ***\n":
                inheader = 0
        else:
            if line == "\037\014\012":
                msg = "\r\n".join(current)
                result.append(msg)
                inheader = 1
                del current[:]
            else:
                current.append(line[:-1])
    f.close()
    return result

class Get_Mails:
    def __init__(self, username_to_filename):
        self.__username_to_filename = username_to_filename

    def get(self, username):
        fname = self.__username_to_filename(username)
        print "fname is %s" %fname
        try:
            f = open(fname)
            read = (f.read(1) == 'F') and read_mbox
            f.close()
            return read(fname)
        except IOError:
            traceback.print_exc()
            raise Error, "Invalid mail box"

if __name__ == '__main__':
    import sys, os
    
    if not (3 <= len(sys.argv) <= 4):
        print sys.argv[0], "MAILBOX-DIR", "PASSWD", "[PORT]"
        print ("\n"
               "This is a sample POP3 server program.  It accepts any user\n"
               "whose name consists of alnums including '-', '_' and '.'.\n"
               "PASSWD will be applied to every user.\n"
               "In MAILBOX-DIR directory, a file of the same name as the\n"
               "user will be read as RMAIL or mbox to retrieve messages.\n"
               "The file will not be modified even if you delete messages\n"
               "via POP3, though."
               )
        sys.exit(1)
    user_to_file = lambda user: os.path.join(sys.argv[1], user)
    server = PopServer(lambda user: not [ 1 for x in user if not x.isalnum()
                                          and x not in ("-", "_", ".") ],
                       lambda user, passwd: passwd == sys.argv[2],
                       Get_Mails(user_to_file).get)
    if len(sys.argv) < 4:
        server.main_loop()
    else:
        server.main_loop(int(sys.argv[3]))
