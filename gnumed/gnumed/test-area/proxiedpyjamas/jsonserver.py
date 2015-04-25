
# Originally taken from:
# http://code.activestate.com/recipes/552751/
# thanks to david decotigny

# Heavily based on the XML-RPC implementation in python.
# Based on the json-rpc specs: http://json-rpc.org/wiki/specification
# The main deviation is on the error treatment. The official spec
# would set the 'error' attribute to a string. This implementation
# sets it to a dictionary with keys: message/traceback/type

import cjson
import SocketServer
import SimpleHTTPServer
import BaseHTTPServer
import sys
import traceback
import socket
import os
import cgi
import urllib
try:
    import fcntl
except ImportError:
    fcntl = None
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class CloseConnection(Exception):
    pass


###
### Server code
###
import SimpleXMLRPCServer

def _quote_html(html):
    return html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

class SimpleJSONRPCDispatcher(SimpleXMLRPCServer.SimpleXMLRPCDispatcher):
    def _marshaled_dispatch(self, data, dispatch_method = None):
        id = None
        try:
            print "about to decode.  pid:", os.getpid(), repr(data)
            req = cjson.decode(data)
            method = req['method']
            params = req['params'] or ()
            id     = req['id']
            print "decoded and about to call. pid:", os.getpid(), method, params

            close_connection = False
            try:
                if dispatch_method is not None:
                    result = dispatch_method(method, params)
                else:
                    result = self._dispatch(method, params)
            except CloseConnection, e:
                close_connection = True
                result = e.args[0]
            print "result", close_connection, result
            response = dict(id=id, result=result, error=None)
        except:
            extpe, exv, extrc = sys.exc_info()
            err = dict(type=str(extpe),
                       message=str(exv),
                       traceback=''.join(traceback.format_tb(extrc)))
            response = dict(id=id, result=None, error=err)
        try:
            print "response", response
            return (cjson.encode(response), close_connection)
        except:
            extpe, exv, extrc = sys.exc_info()
            err = dict(type=str(extpe),
                       message=str(exv),
                       traceback=''.join(traceback.format_tb(extrc)))
            response = dict(id=id, result=None, error=err)
            return (cjson.encode(response), close_connection)


class SimpleJSONRPCRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """Simple JSONRPC request handler class and HTTP GET Server

    Handles all HTTP POST requests and attempts to decode them as
    JSONRPC requests.

    Handles all HTTP GET requests and serves the content from the
    current directory.

    """

    # Class attribute listing the accessible path components;
    # paths not on this list will result in a 404 error.
    rpc_paths = ('/', '/JSON')

    def is_rpc_path_valid(self):
        if self.rpc_paths:
            return self.path in self.rpc_paths
        else:
            # If .rpc_paths is empty, just assume all paths are legal
            return True

    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        print "send_head. pid:", os.getpid()
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        if ctype.startswith('text/'):
            mode = 'r'
        else:
            mode = 'rb'
        try:
            f = open(path, mode)
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        if self.request_version == "HTTP/1.1":
            self.send_header("Connection", "keep-alive")

        self.end_headers()
        return f

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = StringIO()
        displaypath = cgi.escape(urllib.unquote(self.path))
        f.write(u"<title>Directory listing for %s</title>\n" % displaypath)
        f.write(u"<h2>Directory listing for %s</h2>\n" % displaypath)
        f.write(u"<hr>\n<ul>\n")
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write(u'<li><a href="%s">%s</a>\n'
                    % (urllib.quote(linkname), cgi.escape(displayname)))
        f.write(u"</ul>\n<hr>\n")
        f.write(u"\n<hr>\nCookies: %s\n<hr>\n" % str(self.headers.get("Cookie", None)))
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        if self.request_version == "HTTP/1.1":
            self.send_header("Connection", "keep-alive")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def send_error(self, code, message=None):
        """Send and log an error reply.

        Arguments are the error code, and a detailed message.
        The detailed message defaults to the short entry matching the
        response code.

        This sends an error response (so it must be called before any
        output has been generated), logs the error, and finally sends
        a piece of HTML explaining the error to the user.

        """

        try:
            short, long = self.responses[code]
        except KeyError:
            short, long = '???', '???'
        if message is None:
            message = short
        explain = long
        self.log_error("code %d, message %s", code, message)
        # using _quote_html to prevent Cross Site Scripting attacks (see bug #1100201)
        content = (self.error_message_format %
                   {'code': code, 'message': _quote_html(message), 'explain': explain})
        self.send_response(code, message)
        self.send_header("Content-Type", "text/html")
        if self.command != 'HEAD' and code >= 200 and code not in (204, 304):
            self.send_header("Content-Length", str(len(content)))
        if self.request_version == "HTTP/1.1":
            self.send_header("Connection", "keep-alive")
        else:
            self.send_header('Connection', 'close')
        self.end_headers()
        if self.command != 'HEAD' and code >= 200 and code not in (204, 304):
            self.wfile.write(content)

    def do_POST(self):
        """Handles the HTTP POST request.

        Attempts to interpret all HTTP POST requests as XML-RPC calls,
        which are forwarded to the server's _dispatch method for handling.
        """

        self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        # Check that the path is legal
        if not self.is_rpc_path_valid():
            self.report_404()
            return

        try:
            # Get arguments by reading body of request.
            # We read this in chunks to avoid straining
            # socket.read(); around the 10 or 15Mb mark, some platforms
            # begin to have problems (bug #792570).
            max_chunk_size = 10*1024*1024
            size_remaining = int(self.headers["content-length"])
            L = []
            while size_remaining:
                chunk_size = min(size_remaining, max_chunk_size)
                L.append(self.rfile.read(chunk_size))
                size_remaining -= len(L[-1])
            data = ''.join(L)

            # In previous versions of SimpleXMLRPCServer, _dispatch
            # could be overridden in this class, instead of in
            # SimpleXMLRPCDispatcher. To maintain backwards compatibility,
            # check to see if a subclass implements _dispatch and dispatch
            # using that method if present.
            response, close_connection = self.server._marshaled_dispatch(
                                data, getattr(self, '_dispatch', None)
                                                                        )
        except: # This should only happen if the module is buggy
            # internal error, report as HTTP server error
            self.send_response(500)
            self.end_headers()
            return
        # got a valid JSONRPC response
        self.send_response(200)
        self.send_header("Content-type", "text/x-json")
        self.send_header("Connection", "keep-alive")
        self.send_header("Content-length", str(len(response)))
        self.end_headers()
        print "response", repr(response)
        self.wfile.write(response)

        self.wfile.flush()
        print "flushed"
        if close_connection:
            self.connection.shutdown(1)

    def report_404 (self):
            # Report a 404 error
        self.send_response(404)
        response = 'No such page'
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)
        # shut down the connection
        self.wfile.flush()
        self.connection.shutdown(1)

    def log_request(self, code='-', size='-'):
        """Selectively log an accepted request."""

        if self.server.logRequests:
            BaseHTTPServer.BaseHTTPRequestHandler.log_request(self, code, size)


class SimpleForkingJSONRPCServer(SocketServer.ForkingTCPServer,
                          SimpleJSONRPCDispatcher):
    """Simple JSON-RPC server.

    Simple JSON-RPC server that allows functions and a single instance
    to be installed to handle requests. The default implementation
    attempts to dispatch JSON-RPC calls to the functions or instance
    installed in the server. Override the _dispatch method inhereted
    from SimpleJSONRPCDispatcher to change this behavior.
    """

    allow_reuse_address = True

    def __init__(self, addr, requestHandler=SimpleJSONRPCRequestHandler,
                 logRequests=True):
        self.logRequests = logRequests

        SimpleJSONRPCDispatcher.__init__(self, allow_none=True, encoding=None)
        SocketServer.ForkingTCPServer.__init__(self, addr, requestHandler)

        # [Bug #1222790] If possible, set close-on-exec flag; if a
        # method spawns a subprocess, the subprocess shouldn't have
        # the listening socket open.
        if fcntl is not None and hasattr(fcntl, 'FD_CLOEXEC'):
            flags = fcntl.fcntl(self.fileno(), fcntl.F_GETFD)
            flags |= fcntl.FD_CLOEXEC
            fcntl.fcntl(self.fileno(), fcntl.F_SETFD, flags)

class SimpleJSONRPCServer(SocketServer.ThreadingTCPServer,
                          SimpleJSONRPCDispatcher):
    """Simple JSON-RPC server.

    Simple JSON-RPC server that allows functions and a single instance
    to be installed to handle requests. The default implementation
    attempts to dispatch JSON-RPC calls to the functions or instance
    installed in the server. Override the _dispatch method inhereted
    from SimpleJSONRPCDispatcher to change this behavior.
    """

    allow_reuse_address = True

    def __init__(self, addr, requestHandler=SimpleJSONRPCRequestHandler,
                 logRequests=True):
        self.logRequests = logRequests

        SimpleJSONRPCDispatcher.__init__(self, allow_none=True, encoding=None)
        SocketServer.ThreadingTCPServer.__init__(self, addr, requestHandler)

        # [Bug #1222790] If possible, set close-on-exec flag; if a
        # method spawns a subprocess, the subprocess shouldn't have
        # the listening socket open.
        if fcntl is not None and hasattr(fcntl, 'FD_CLOEXEC'):
            flags = fcntl.fcntl(self.fileno(), fcntl.F_GETFD)
            flags |= fcntl.FD_CLOEXEC
            fcntl.fcntl(self.fileno(), fcntl.F_SETFD, flags)


###
### Client code
###
import xmlrpclib

class ResponseError(xmlrpclib.ResponseError):
    pass
class Fault(xmlrpclib.ResponseError):
    pass

def _get_response(file, sock):
    data = ""
    while 1:
        if sock:
            response = sock.recv(1024)
        else:
            response = file.read(1024)
        if not response:
            break
        data += response

    file.close()

    return data

class Transport(xmlrpclib.Transport):
    def _parse_response(self, file, sock):
        return _get_response(file, sock)

class SafeTransport(xmlrpclib.SafeTransport):
    def _parse_response(self, file, sock):
        return _get_response(file, sock)

class ServerProxy:
    def __init__(self, uri, id=None, transport=None, use_datetime=0):
        # establish a "logical" server connection

        # get the url
        import urllib
        type, uri = urllib.splittype(uri)
        if type not in ("http", "https"):
            raise IOError, "unsupported JSON-RPC protocol"
        self.__host, self.__handler = urllib.splithost(uri)
        if not self.__handler:
            self.__handler = "/JSON"

        if transport is None:
            if type == "https":
                transport = SafeTransport(use_datetime=use_datetime)
            else:
                transport = Transport(use_datetime=use_datetime)

        self.__transport = transport
        self.__id        = id

    def __request(self, methodname, params):
        # call a method on the remote server

        request = cjson.encode(dict(id=self.__id, method=methodname,
                                    params=params))

        data = self.__transport.request(
            self.__host,
            self.__handler,
            request,
            verbose=False
            )

        response = cjson.decode(data)

        if response["id"] != self.__id:
            raise ResponseError("Invalid request id (is: %s, expected: %s)" \
                                % (response["id"], self.__id))
        if response["error"] is not None:
            raise Fault("JSON Error", response["error"])
        return response["result"]

    def __repr__(self):
        return (
            "<ServerProxy for %s%s>" %
            (self.__host, self.__handler)
            )

    __str__ = __repr__

    def __getattr__(self, name):
        # magic method dispatcher
        return xmlrpclib._Method(self.__request, name)


if __name__ == '__main__':
    if not len(sys.argv) > 1:
        import socket
        print 'Running JSON-RPC server on port 8000'
        server = SimpleJSONRPCServer(("localhost", 8000))
        server.register_function(pow)
        server.register_function(lambda x,y: x+y, 'add')
        server.register_function(lambda x: x, 'echo')
        server.serve_forever()
    else:
        remote = ServerProxy(sys.argv[1])
        print 'Using connection', remote

        print repr(remote.add(1, 2))
        aaa = remote.add
        print repr(remote.pow(2, 4))
        print aaa(5, 6)

        try:
            # Invalid parameters
            aaa(5, "toto")
            print "Successful execution of invalid code"
        except Fault:
            pass

        try:
            # Invalid parameters
            aaa(5, 6, 7)
            print "Successful execution of invalid code"
        except Fault:
            pass

        try:
            # Invalid method name
            print repr(remote.powx(2, 4))
            print "Successful execution of invalid code"
        except Fault:
            pass
