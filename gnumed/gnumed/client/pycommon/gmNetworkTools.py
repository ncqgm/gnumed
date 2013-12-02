# -*- coding: utf-8 -*-
__doc__ = """GNUmed internetworking tools."""

#===========================================================================
__author__ = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

# std libs
import sys
import os.path
import logging
import urllib2 as wget
import urllib
import MimeWriter
import mimetypes
import mimetools
import StringIO
import zipfile
import webbrowser


# GNUmed libs
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLog2
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmCfg2


_log = logging.getLogger('gm.net')

#===========================================================================
# browser access
#---------------------------------------------------------------------------
def open_url_in_browser(url, new=2, autoraise=True, *args, **kwargs):
	# url, new=0, autoraise=True
	try:
		webbrowser.open(url, new = new, autoraise = autoraise, **kwargs)
	except (webbrowser.Error, OSError, UnicodeEncodeError):
		_log.exception('error calling browser with url=%s', url)
		return False
	return True
#===========================================================================
def download_file(url, filename=None, suffix=None):

	if filename is None:
		filename = gmTools.get_unique_filename(prefix = 'gm-dl-', suffix = suffix)
	_log.debug('downloading [%s] into [%s]', url, filename)

	try:
		dl_name, headers = urllib.urlretrieve(url, filename)
	except (ValueError, OSError, IOError):
		_log.exception('cannot download from [%s]', url)
		gmLog2.log_stack_trace()
		return None

	_log.debug(u'%s' % headers)
	return dl_name
#===========================================================================
# data pack handling
#---------------------------------------------------------------------------
def download_data_packs_list(url, filename=None):
	return download_file(url, filename = filename, suffix = 'conf')
#---------------------------------------------------------------------------
def download_data_pack(pack_url, filename=None, md5_url=None):

	_log.debug('downloading data pack from: %s', pack_url)
	dp_fname = download_file(pack_url, filename = filename, suffix = 'zip')
	_log.debug('downloading MD5 from: %s', md5_url)
	md5_fname = download_file(md5_url, filename = dp_fname + u'.md5')

	md5_file = open(md5_fname, 'rU')
	md5_expected = md5_file.readline().strip('\n')
	md5_file.close()
	_log.debug('expected MD5: %s', md5_expected)
	md5_calculated = gmTools.file2md5(dp_fname, return_hex = True)
	_log.debug('calculated MD5: %s', md5_calculated)

	if md5_calculated != md5_expected:
		_log.error('mismatch of expected vs calculated MD5: [%s] vs [%s]', md5_expected, md5_calculated)
		return (False, (md5_expected, md5_calculated))

	return True, dp_fname
#---------------------------------------------------------------------------
def unzip_data_pack(filename=None):

	unzip_dir = os.path.splitext(filename)[0]
	_log.debug('unzipping data pack into [%s]', unzip_dir)
	gmTools.mkdir(unzip_dir)
	try:
		data_pack = zipfile.ZipFile(filename, 'r')
	except (zipfile.BadZipfile):
		_log.exception('cannot unzip data pack [%s]', filename)
		gmLog2.log_stack_trace()
		return None

	data_pack.extractall(unzip_dir)

	return unzip_dir
#---------------------------------------------------------------------------
def install_data_pack(data_pack=None, conn=None):
	from Gnumed.pycommon import gmPsql
	psql = gmPsql.Psql(conn)
	sql_script = os.path.join(data_pack['unzip_dir'], 'install-data-pack.sql')
	if psql.run(sql_script) == 0:
		curs = conn.cursor()
		curs.execute(u'select gm.log_script_insertion(%(name)s, %(ver)s)', {'name': data_pack['pack_url'], 'ver': u'current'})
		curs.close()
		conn.commit()
		return True

	_log.error('error installing data pack: %s', data_pack)
	return False
#---------------------------------------------------------------------------
def download_data_pack_old(url, target_dir=None):

	if target_dir is None:
		target_dir = gmTools.get_unique_filename(prefix = 'gm-dl-')

	_log.debug('downloading [%s]', url)
	_log.debug('unpacking into [%s]', target_dir)

	gmTools.mkdir(directory = target_dir)

	# FIXME: rewrite to use urllib.urlretrieve() and 

	paths = gmTools.gmPaths()
	local_script = os.path.join(paths.local_base_dir, '..', 'external-tools', 'gm-download_data')

	candidates = [u'gm-download_data', u'gm-download_data.bat', local_script, u'gm-download_data.bat']
	args = u' %s %s' % (url, target_dir)

	success = gmShellAPI.run_first_available_in_shell (
		binaries = candidates,
		args = args,
		blocking = True,
		run_last_one_anyway = True
	)

	if success:
		return True, target_dir

	_log.error('download failed')
	return False, None
#===========================================================================
# client update handling
#---------------------------------------------------------------------------
def compare_versions(left_version, right_version):
	"""
	 0: left == right
	-1: left < right
	 1: left > right
	"""
	if left_version == right_version:
		_log.debug('same version: [%s] = [%s]', left_version, right_version)
		return 0

	left_parts = left_version.split('.')
	right_parts = right_version.split('.')

	tmp, left_major = gmTools.input2decimal(u'%s.%s' % (left_parts[0], left_parts[1]))
	tmp, right_major = gmTools.input2decimal(u'%s.%s' % (right_parts[0], right_parts[1]))

	if left_major < right_major:
		_log.debug('left version [%s] < right version [%s]: major part', left_version, right_version)
		return -1

	if left_major > right_major:
		_log.debug('left version [%s] > right version [%s]: major part', left_version, right_version)
		return 1

	tmp, left_part3 = gmTools.input2decimal(left_parts[2].replace('rc', '0.'))
	tmp, right_part3 = gmTools.input2decimal(right_parts[2].replace('rc', '0.'))

	if left_part3 < right_part3:
		_log.debug('left version [%s] < right version [%s]: minor part', left_version, right_version)
		return -1

	if left_part3 > right_part3:
		_log.debug('left version [%s] > right version [%s]: minor part', left_version, right_version)
		return 1

	return 0
#---------------------------------------------------------------------------
def check_for_update(url=None, current_branch=None, current_version=None, consider_latest_branch=False):
	"""Check for new releases at <url>.

	Returns (bool, text).
	True: new release available
	False: up to date
	None: don't know
	"""
	if current_version == u'GIT HEAD':
		_log.debug('GIT HEAD always up to date')
		return (False, None)

	try:
		remote_file = wget.urlopen(url)
	except (wget.URLError, ValueError, OSError):
		_log.exception("cannot retrieve version file from [%s]", url)
		return (None, _('Cannot retrieve version information from:\n\n%s') % url)

	_log.debug('retrieving version information from [%s]', url)

	cfg = gmCfg2.gmCfgData()
	try:
		cfg.add_stream_source(source = 'gm-versions', stream = remote_file)
	except (UnicodeDecodeError):
		remote_file.close()
		_log.exception("cannot read version file from [%s]", url)
		return (None, _('Cannot read version information from:\n\n%s') % url)

	remote_file.close()

	latest_branch = cfg.get('latest branch', 'branch', source_order = [('gm-versions', 'return')])
	latest_release_on_latest_branch = cfg.get('branch %s' % latest_branch, 'latest release', source_order = [('gm-versions', 'return')])
	latest_release_on_current_branch = cfg.get('branch %s' % current_branch, 'latest release', source_order = [('gm-versions', 'return')])

	cfg.remove_source('gm-versions')

	_log.info('current release: %s', current_version)
	_log.info('current branch: %s', current_branch)
	_log.info('latest release on current branch: %s', latest_release_on_current_branch)
	_log.info('latest branch: %s', latest_branch)
	_log.info('latest release on latest branch: %s', latest_release_on_latest_branch)

	# anything known ?
	no_release_information_available = (
		(
			(latest_release_on_current_branch is None) and
			(latest_release_on_latest_branch is None)
		) or (
			not consider_latest_branch and
			(latest_release_on_current_branch is None)
		)
	)
	if no_release_information_available:
		_log.warning('no release information available')
		msg = _('There is no version information available from:\n\n%s') % url
		return (None, msg)

	# up to date ?
	if consider_latest_branch:
		_log.debug('latest branch taken into account')
		if latest_release_on_latest_branch is None:
			if compare_versions(latest_release_on_current_branch, current_version) in [-1, 0]:
				_log.debug('up to date: current version >= latest version on current branch and no latest branch available')
				return (False, None)
		else:
			if compare_versions(latest_release_on_latest_branch, current_version) in [-1, 0]:
				_log.debug('up to date: current version >= latest version on latest branch')
				return (False, None)
	else:
		_log.debug('latest branch not taken into account')
		if compare_versions(latest_release_on_current_branch, current_version) in [-1, 0]:
			_log.debug('up to date: current version >= latest version on current branch')
			return (False, None)

	new_release_on_current_branch_available = (
		(latest_release_on_current_branch is not None) and
		(compare_versions(latest_release_on_current_branch, current_version) == 1)
	)
	_log.info('%snew release on current branch available', gmTools.bool2str(new_release_on_current_branch_available, '', 'no '))

	new_release_on_latest_branch_available = (
		(latest_branch is not None)
			and
		(
			(latest_branch > current_branch) or (
				(latest_branch == current_branch) and
				(compare_versions(latest_release_on_latest_branch, current_version) == 1)
			)
		)
	)
	_log.info('%snew release on latest branch available', gmTools.bool2str(new_release_on_latest_branch_available, '', 'no '))

	if not (new_release_on_current_branch_available or new_release_on_latest_branch_available):
		_log.debug('up to date: no new releases available')
		return (False, None)

	# not up to date
	msg = _('A new version of GNUmed is available.\n\n')
	msg += _(' Your current version: "%s"\n') % current_version
	if consider_latest_branch:
		if new_release_on_current_branch_available:
			msg += u'\n'
			msg += _(' New version: "%s"') % latest_release_on_current_branch
			msg += u'\n'
			msg += _(' - bug fixes only\n')
			msg += _(' - database fixups may be needed\n')
		if new_release_on_latest_branch_available:
			if current_branch != latest_branch:
				msg += u'\n'
				msg += _(' New version: "%s"') % latest_release_on_latest_branch
				msg += u'\n'
				msg += _(' - bug fixes and new features\n')
				msg += _(' - database upgrade required\n')
	else:
		msg += u'\n'
		msg += _(' New version: "%s"') % latest_release_on_current_branch
		msg += u'\n'
		msg += _(' - bug fixes only\n')
		msg += _(' - database fixups may be needed\n')

	msg += u'\n\n'
	msg += _(
		'Note, however, that this version may not yet\n'
		'be available *pre-packaged* for your system.'
	)

	msg += u'\n\n'
	msg += _('Details are found on <http://wiki.gnumed.de>.\n')
	msg += u'\n'
	msg += _('Version information loaded from:\n\n %s') % url

	return (True, msg)
#===========================================================================
# mail handling
#---------------------------------------------------------------------------
default_mail_sender = u'gnumed@gmx.net'
default_mail_receiver = u'gnumed-devel@gnu.org'
default_mail_server = u'mail.gmx.net'

def send_mail(sender=None, receiver=None, message=None, server=None, auth=None, debug=False, subject=None, encoding='quoted-printable', attachments=None):
	# FIXME: How to generate and send mails: a step by step tutorial
	# FIXME: http://groups.google.com/group/comp.lang.python/browse_thread/thread/e0793c1007361398/
	# FIXME: google for aspineux blog

	if message is None:
		return False

	message = message.lstrip().lstrip('\r\n').lstrip()

	if sender is None:
		sender = default_mail_sender

	if receiver is None:
		receiver = [default_mail_receiver]

	if server is None:
		server = default_mail_server

	if subject is None:
		subject = u'gmTools.py: send_mail() test'

	msg = StringIO.StringIO()
	writer = MimeWriter.MimeWriter(msg)
	writer.addheader('To', u', '.join(receiver))
	writer.addheader('From', sender)
	writer.addheader('Subject', subject[:50].replace('\r', '/').replace('\n', '/'))
	writer.addheader('MIME-Version', '1.0')

	writer.startmultipartbody('mixed')

	# start with a text/plain part
	part = writer.nextpart()
	body = part.startbody('text/plain')
	part.flushheaders()
	body.write(message.encode(encoding))

	# now add the attachments
	if attachments is not None:
		for a in attachments:
			filename = os.path.basename(a[0])
			try:
				mtype = a[1]
				encoding = a[2]
			except IndexError:
				mtype, encoding = mimetypes.guess_type(a[0])
				if mtype is None:
					mtype = 'application/octet-stream'
					encoding = 'base64'
				elif mtype == 'text/plain':
					encoding = 'quoted-printable'
				else:
					encoding = 'base64'

			part = writer.nextpart()
			part.addheader('Content-Transfer-Encoding', encoding)
			body = part.startbody("%s; name=%s" % (mtype, filename))
			mimetools.encode(open(a[0], 'rb'), body, encoding)

	writer.lastpart()

	import smtplib
	session = smtplib.SMTP(server)
	session.set_debuglevel(debug)
	if auth is not None:
		session.login(auth['user'], auth['password'])
	refused = session.sendmail(sender, receiver, msg.getvalue())
	session.quit()
	msg.close()
	if len(refused) != 0:
		_log.error("refused recipients: %s" % refused)
		return False

	return True
#===========================================================================
# main
#---------------------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	#-----------------------------------------------------------------------
	def test_send_mail():
		msg = u"""
To: %s
From: %s
Subject: gmTools test suite mail

This is a test mail from the gmTools.py module.
""" % (default_mail_receiver, default_mail_sender)
		print "mail sending succeeded:", send_mail (
			receiver = [default_mail_receiver, u'karsten.hilbert@gmx.net'],
			message = msg,
			auth = {'user': default_mail_sender, 'password': u'gnumed-at-gmx-net'}, # u'gm/bugs/gmx'
			debug = True,
			attachments = [sys.argv[0]]
		)
	#-----------------------------------------------------------------------
	def test_check_for_update():

		test_data = [
			('http://www.gnumed.de/downloads/gnumed-versions.txt', None, None, False),
			('file:///home/ncq/gm-versions.txt', None, None, False),
			('file:///home/ncq/gm-versions.txt', '0.2', '0.2.8.1', False),
			('file:///home/ncq/gm-versions.txt', '0.2', '0.2.8.1', True),
			('file:///home/ncq/gm-versions.txt', '0.2', '0.2.8.5', True)
		]

		for test in test_data:
			print "arguments:", test
			found, msg = check_for_update(test[0], test[1], test[2], test[3])
			print msg

		return
	#-----------------------------------------------------------------------
	def test_dl_data_pack():
		#url = 'file:./x-data_pack.zip'
		#url = 'missing-file.zip'
		url = 'gmTools.py'
		dl_name = download_data_pack(url)
		print url, "->", dl_name
		unzip_dir = unzip_data_pack(dl_name)
		print "unzipped into", unzip_dir
	#-----------------------------------------------------------------------
	def test_browser():
		success = open_url_in_browser(sys.argv[2])
		print success
		open_url_in_browser(sys.argv[2], abc=222)
	#-----------------------------------------------------------------------
	#test_check_for_update()
	#test_send_mail()
	#test_dl_data_pack()
	test_browser()

#===========================================================================
