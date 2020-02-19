#!/usr/bin/env python

__doc__ = """GNUmed web user interface server launcher.
"""
#==========================================================
__version__ = "$Revision: 0.1 $"
__author__  = "S. Hilbert <Sebastian.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

# stdlib
import re, sys, time, os, cPickle, zlib, locale, os.path
import datetime as pyDT, shutil, logging, urllib2

# json-rpc
from jsonserver import SimpleForkingJSONRPCServer, CloseConnection

# GNUmed libs
from Gnumed.pycommon import gmI18N, gmTools, gmDateTime, gmHooks
from Gnumed.pycommon import gmLoginInfo, gmBackendListener, gmTools, gmCfg2
from Gnumed.pycommon import gmCfg2, gmI18N, gmDispatcher, gmBusinessDBObject
from Gnumed.pycommon.gmBusinessDBObject import jsonclasshintify
from Gnumed.pycommon import gmPG2
from Gnumed.business import gmDocuments
from Gnumed.business import gmPerson
from Gnumed.business import gmStaff
from Gnumed.business import gmProviderInbox
from Gnumed.business import gmPersonSearch


#try:
#   _('dummy-no-need-to-translate-but-make-epydoc-happy')
#except NameError:
#   _ = lambda x:x

_cfg = gmCfg2.gmCfgData()
_provider = None
_scripting_listener = None

_log = logging.getLogger('gm.main')
_log.info(__version__)
_log.info('web GUI framework')

#================================================================
# convenience functions
#----------------------------------------------------------------
def connect_to_database(login_info=None, max_attempts=3, expected_version=None, require_version=True):
    """Display the login dialog and try to log into the backend.

    - up to max_attempts times
    - returns True/False
    """
    from Gnumed.pycommon import gmPG2
    # force programmer to set a valid expected_version
    expected_hash = gmPG2.known_schema_hashes[expected_version]
    client_version = _cfg.get(option = u'client_version')
    global current_db_name
    current_db_name = u'gnumed_v%s' % expected_version

    attempt = 0

    while attempt < max_attempts:

        _log.debug('login attempt %s of %s', (attempt+1), max_attempts)

        connected = False

        login = login_info
        if login is None:
            _log.info("did not provide a login information")

        # try getting a connection to verify the DSN works
        dsn = gmPG2.make_psycopg2_dsn (
            database = login.database,
            host = login.host,
            port = login.port,
            user = login.user,
            password = login.password
        )
        try:
            #conn = gmPG2.get_raw_connection(dsn = dsn, verbose = True, readonly = True)
            conn = gmPG2.get_raw_connection(dsn = dsn, verbose = True, readonly = True)
            connected = True

        except gmPG2.cAuthenticationError, e:
            attempt += 1
            _log.error(u"login attempt failed: %s", e)
            if attempt < max_attempts:
                if (u'host=127.0.0.1' in (u'%s' % e)) or (u'host=' not in (u'%s' % e)):
                    msg = _(
                        'Unable to connect to database:\n\n'
                        '%s\n\n'
                        "Are you sure you have got a local database installed ?\n"
                        '\n'
                        "Please retry with proper credentials or cancel.\n"
                        '\n'
                        'You may also need to check the PostgreSQL client\n'
                        'authentication configuration in pg_hba.conf. For\n'
                        'details see:\n'
                        '\n'
                        'wiki.gnumed.de/bin/view/Gnumed/ConfigurePostgreSQL'
                    )
                else:
                    msg = _(
                        "Unable to connect to database:\n\n"
                        "%s\n\n"
                        "Please retry with proper credentials or cancel.\n"
                        "\n"
                        'You may also need to check the PostgreSQL client\n'
                        'authentication configuration in pg_hba.conf. For\n'
                        'details see:\n'
                        '\n'
                        'wiki.gnumed.de/bin/view/Gnumed/ConfigurePostgreSQL'
                    )
                msg = msg % e
                msg = re.sub(r'password=[^\s]+', u'password=%s' % gmTools.u_replacement_character, msg)
                gmGuiHelpers.gm_show_error (
                    msg,
                    _('Connecting to backend')
                )
            del e
            continue

        except gmPG2.dbapi.OperationalError, e:
            _log.error(u"login attempt failed: %s", e)
            msg = _(
                "Unable to connect to database:\n\n"
                "%s\n\n"
                "Please retry another backend / user / password combination !\n"
            ) % gmPG2.extract_msg_from_pg_exception(e)
            msg = re.sub(r'password=[^\s]+', u'password=%s' % gmTools.u_replacement_character, msg)
            gmGuiHelpers.gm_show_error (
                msg,
                _('Connecting to backend')
            )
            del e
            continue


#       compatible = gmPG2.database_schema_compatible(version = expected_version)
#       if compatible or not require_version:
            #dlg.panel.save_state()
#           continue

#       if not compatible:
#           connected_db_version = gmPG2.get_schema_version()
#           msg = msg_generic % (
#               client_version,
#               connected_db_version,
#               expected_version,
#               gmTools.coalesce(login.host, '<localhost>'),
#               login.database,
#               login.user
#           )

#           if require_version:
            #   gmGuiHelpers.gm_show_error(msg + msg_fail, _('Verifying database version'))
#               pass
            #gmGuiHelpers.gm_show_info(msg + msg_override, _('Verifying database version'))

#       # FIXME: make configurable
#       max_skew = 1        # minutes
#       if _cfg.get(option = 'debug'):
#           max_skew = 10
#       if not gmPG2.sanity_check_time_skew(tolerance = (max_skew * 60)):
#           if _cfg.get(option = 'debug'):
#               gmGuiHelpers.gm_show_warning(msg_time_skew_warn % max_skew, _('Verifying database settings'))
#           else:
#               gmGuiHelpers.gm_show_error(msg_time_skew_fail % max_skew, _('Verifying database settings'))
#               continue

#       sanity_level, message = gmPG2.sanity_check_database_settings()
#       if sanity_level != 0:
#           gmGuiHelpers.gm_show_error((msg_insanity % message), _('Verifying database settings'))
#           if sanity_level == 2:
#               continue

#       gmExceptionHandlingWidgets.set_is_public_database(login.public_db)
#       gmExceptionHandlingWidgets.set_helpdesk(login.helpdesk)

        listener = gmBackendListener.gmBackendListener(conn = conn)
        break

    #dlg.Destroy()

    return connected

#----------------------------------------------------------------------------
#internal helper functions
#----------------------------------------------------
def __get_backend_profiles():
        """Get server profiles from the configuration files.

        1) from system-wide file
        2) from user file

        Profiles in the user file which have the same name
        as a profile in the system file will override the
        system file.
        """
        # find active profiles
        src_order = [
            (u'explicit', u'extend'),
            (u'system', u'extend'),
            (u'user', u'extend'),
            (u'workbase', u'extend')
        ]

        profile_names = gmTools.coalesce (
            _cfg.get(group = u'backend', option = u'profiles', source_order = src_order),
            []
        )

        # find data for active profiles
        src_order = [
            (u'explicit', u'return'),
            (u'workbase', u'return'),
            (u'user', u'return'),
            (u'system', u'return')
        ]

        profiles = {}

        for profile_name in profile_names:
            # FIXME: once the profile has been found always use the corresponding source !
            # FIXME: maybe not or else we cannot override parts of the profile
            profile = cBackendProfile()
            profile_section = 'profile %s' % profile_name

            profile.name = profile_name
            profile.host = gmTools.coalesce(_cfg.get(profile_section, u'host', src_order), u'').strip()
            port = gmTools.coalesce(_cfg.get(profile_section, u'port', src_order), 5432)
            try:
                profile.port = int(port)
                if profile.port < 1024:
                    raise ValueError('refusing to use priviledged port (< 1024)')
            except ValueError:
                _log.warning('invalid port definition: [%s], skipping profile [%s]', port, profile_name)
                continue
            profile.database = gmTools.coalesce(_cfg.get(profile_section, u'database', src_order), u'').strip()
            if profile.database == u'':
                _log.warning('database name not specified, skipping profile [%s]', profile_name)
                continue
            profile.encoding = gmTools.coalesce(_cfg.get(profile_section, u'encoding', src_order), u'UTF8')
            profile.public_db = bool(_cfg.get(profile_section, u'public/open access', src_order))
            profile.helpdesk = _cfg.get(profile_section, u'help desk', src_order)

            label = u'%s (%s@%s)' % (profile_name, profile.database, profile.host)
            profiles[label] = profile

        # sort out profiles with incompatible database versions if not --debug
        # NOTE: this essentially hardcodes the database name in production ...
        if not (_cfg.get(option = 'debug') or current_db_name.endswith('_devel')):
            profiles2remove = []
            for label in profiles:
                if profiles[label].database != current_db_name:
                    profiles2remove.append(label)
            for label in profiles2remove:
                del profiles[label]

        if len(profiles) == 0:
            host = u'publicdb.gnumed.de'
            label = u'public GNUmed database (%s@%s)' % (current_db_name, host)
            profiles[label] = cBackendProfile()
            profiles[label].name = label
            profiles[label].host = host
            profiles[label].port = 5432
            profiles[label].database = current_db_name
            profiles[label].encoding = u'UTF8'
            profiles[label].public_db = True
            profiles[label].helpdesk = u'http://wiki.gnumed.de'

        return profiles

# ------------------------------------------------------------
def GetLoginInfo(username=None, password=None, backend=None ):
    
    # username is provided through the web interface
    # password is provided
    # we need the profile

    """convenience function for compatibility with gmLoginInfo.LoginInfo"""
    from Gnumed.pycommon import gmLoginInfo
    #if not self.cancelled:
        # FIXME: do not assume conf file is latin1 !
        #profile = self.__backend_profiles[self._CBOX_profile.GetValue().encode('latin1').strip()]
    #self.__backend_profiles = self.__get_backend_profiles()
    __backend_profiles = __get_backend_profiles()
    profile = __backend_profiles[backend.encode('utf8').strip()]
    
    _log.debug(u'backend profile "%s" selected', profile.name)
    _log.debug(u' details: <%s> on %s@%s:%s (%s, %s)',
        username,
        profile.database,
        profile.host,
        profile.port,
        profile.encoding,
        gmTools.bool2subst(profile.public_db, u'public', u'private')
        )
    #_log.debug(u' helpdesk: "%s"', profile.helpdesk)
    login = gmLoginInfo.LoginInfo (
        user = username,
        password = password,
        host = profile.host,
        database = profile.database,
        port = profile.port
        )
    #login.public_db = profile.public_db
    #login.helpdesk = profile.helpdesk
    return login
    
#----------------------------------------------
def _signal_debugging_monitor(*args, **kwargs):
        try:
            kwargs['originated_in_database']
            print '==> got notification from database "%s":' % kwargs['signal']
        except KeyError:
            print '==> received signal from client: "%s"' % kwargs['signal']

        del kwargs['signal']
        for key in kwargs.keys():
            print '    [%s]: %s' % (key, kwargs[key])

#================================================================
class cBackendProfile:
    pass

#================================================================


PYJSDIR = sys._getframe().f_code.co_filename
PYJSDIR = os.path.split(os.path.dirname(PYJSDIR))[0]
PYJSDIR = os.path.join(PYJSDIR, 'pyjamas')

DEFAULT_BACKEND = "GNUmed database on this machine (Linux/Mac) (gnumed_v22@)"

class HTTPServer(SimpleForkingJSONRPCServer):
    '''An application instance containing any number of streams. Except for constructor all methods are generators.'''
    count = 0
    def __init__(self):
        SimpleForkingJSONRPCServer.__init__(self, ("localhost", 60001))

        self.register_function(self.echo)
        self.register_function(self.login)
        self.register_function(self.logout)
        self.register_function(self.search_patient)
        self.register_function(self.get_provider_inbox_data)
        self.register_function(self.get_patient_messages)
        self.register_function(self.get_doc_types)
        self.register_function(self.get_documents)
        self.register_function(self.get_schema_version)
        self.register_function(self.doSomething)

    def echo(self, text):
        return text
    def reverse(self, text):
        return text[::-1]
    def uppercase(self, text):
        return text.upper()
    def lowercase(self,text):
        return text.lower()

    def login(self, username=None, password=None, backend=None):
        from Gnumed.pycommon import gmPG2
        if backend is None:
            backend = DEFAULT_BACKEND
        login_info = GetLoginInfo(username, password, backend)
        override = _cfg.get(option = '--override-schema-check',
                            source_order = [('cli', 'return')])
        cb = _cfg.get(option = 'client_branch')
        expected_version = gmPG2.map_client_branch2required_db_version[cb]
        connected = connect_to_database (
                login_info,
                expected_version = expected_version,
                require_version = not override
            )
        return connected

    def logout(self):
        """ return value is in the exception
        """
        raise CloseConnection(True)

    def search_patient(self, search_term):
        
        self.__person_searcher = gmPersonSearch.cPatientSearcher_SQL()
        # get list of matching ids
        idents = self.__person_searcher.get_identities(search_term)

        if idents is None:
            idents = []

        _log.info("%s matching person(s) found", len(idents))

        # only one matching identity
        if len(idents) == 1:
            self.person = idents[0]
            return jsonclasshintify(self.person)

        # ambiguous - return available choices, to be able to choose from them.
        self.person = None
        return jsonclasshintify(idents)

    def get_patient_messages(self, pk_patient):
        messages = gmProviderInbox.get_inbox_messages(pk_patient=pk_patient)
        return jsonclasshintify(messages)

    def get_provider_inbox_data(self):
        self.provider = gmStaff.gmCurrentProvider(provider=gmStaff.cStaff())
        inbox = gmProviderInbox.cProviderInbox()
        self.__msgs = inbox.messages
        return jsonclasshintify(inbox.messages)

    def get_schema_version(self):
        return gmPG2.get_schema_version()

    def get_documents(self, key):
        doc_folder = gmDocuments.cDocumentFolder(aPKey=key)
        return jsonclasshintify(doc_folder.get_documents())

    def get_doc_types(self):
        return jsonclasshintify(gmDocuments.get_document_types())

    def doSomething(self):
        msg = 'schema version is:' + gmPG2.get_schema_version() +'\n\n'
        msg2 =''
        for item in gmDocuments.get_document_types():
            msg2 = msg2 +'\n' + str(item)
        msg = msg + msg2
        return "<pre>%s</pre>" % msg
    

#==========================================================
# main - launch the GNUmed web client
#----------------------------------------------------------

def main():

    if _cfg.get(option = 'debug'):
        gmDispatcher.connect(receiver = _signal_debugging_monitor)
        _log.debug('gmDispatcher signal monitor activated')

    server = HTTPServer()
    server.serve_forever()

