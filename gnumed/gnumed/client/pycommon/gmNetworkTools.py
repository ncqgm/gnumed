# -*- coding: utf-8 -*-

"""GNUmed internetworking tools."""

#===========================================================================
__author__ = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

# std libs
import sys
import os.path
import logging
import urllib.request
import urllib.error
import zipfile
import webbrowser
import io


# GNUmed libs
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmLog2
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmCfgINI
from Gnumed.pycommon import gmMimeLib


_log = logging.getLogger('gm.net')

#===========================================================================
# browser access
#---------------------------------------------------------------------------
def open_url_in_browser(url:str, new:int=2, autoraise:bool=True, *args, **kwargs) -> bool:
	"""Open an URL in a browser.

	Args:
		url: URL to open
		new: whether to open a new browser, a new tab in a running browser, or a tab OR a browser
	"""
	# new=2: open new tab if possible
	try:
		webbrowser.open(url, new = new, autoraise = autoraise)
	except (webbrowser.Error, OSError, UnicodeEncodeError):
		_log.exception('error calling browser with url=%s', url)
		return False

	return True

#---------------------------------------------------------------------------
def download_file(url, filename=None, suffix=None):
	if filename is None:
		filename = gmTools.get_unique_filename(prefix = 'gm-dl-', suffix = suffix)
	_log.debug('downloading [%s] into [%s]', url, filename)
	try:
		dl_name, headers = urllib.request.urlretrieve(url, filename)
	except (ValueError, OSError, IOError):
		_log.exception('cannot download from [%s]', url)
		gmLog2.log_stack_trace()
		return None

	_log.debug('%s' % headers)
	return dl_name

#---------------------------------------------------------------------------
def mirror_url(url:str, base_dir:str=None, verbose:bool=False) -> str:
	"""Mirror the web*page* at _url_, non-recursively.

	Note: Not for mirroring a *site* (recursively).

	Args:
		url: the URL to mirror
		base_dir: where to store the page and its prerequisites, sandbox dir under tmp_dir if None
	"""
	assert (url is not None), '<url> must not be None'
	_log.debug('mirroring: %s', url)
	if base_dir is None:
		prefix = url.split('://')[-1]
		prefix = prefix.strip(':').strip('/').replace('/', '#')
		prefix = gmTools.fname_sanitize(prefix)
		base_dir = gmTools.mk_sandbox_dir(prefix = prefix + '-')
	_log.debug('base dir: %s', base_dir)
	wget_cmd = [
		'wget',
		'--directory-prefix=%s' % base_dir,
		#'--adjust-extension',
		'--no-remove-listing',
		'--timestamping',
		'--page-requisites',
		'--continue',
		'--convert-links',
		'--user-agent=""',
		'--execute', 'robots=off',
		'--wait=1'
	]
	if verbose:
		wget_cmd.append('--debug')
	wget_cmd.append(url)
	#wget --output-file=logfile
	#'<a href="%s">%s</a>' % (url, url),
	success, ret_code, STDOUT = gmShellAPI.run_process(cmd_line = wget_cmd, timeout = 15, verbose = verbose)
	if success:
		return base_dir

	return None

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
	md5_fname = download_file(md5_url, filename = dp_fname + '.md5')

	md5_file = open(md5_fname, mode = 'rt', encoding = 'utf-8-sig')
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
		curs.execute('select gm.log_script_insertion(%(name)s, %(ver)s)', {'name': data_pack['pack_url'], 'ver': 'current'})
		curs.close()
		conn.commit()
		return True

	_log.error('error installing data pack: %s', data_pack)
	return False

#===========================================================================
# client update handling
#---------------------------------------------------------------------------
def compare_versions(left_version, right_version):
	"""
	 0: left == right
	-1: left < right
	 1: left > right
	"""
	_log.debug('comparing [%s] with [%s]', left_version, right_version)
	if left_version == right_version:
		_log.debug('same version')
		return 0

	if right_version in ['head', 'dev', 'devel']:
		_log.debug('development code')
		return -1

	if left_version in ['head', 'dev', 'devel']:
		_log.debug('development code')
		return 1

	left_parts = left_version.split('.')
	right_parts = right_version.split('.')

	tmp, left_major = gmTools.input2decimal('%s.%s' % (left_parts[0], left_parts[1]))
	tmp, right_major = gmTools.input2decimal('%s.%s' % (right_parts[0], right_parts[1]))

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
	if current_version is None:
		_log.debug('<current_version> is None, currency unknown')
		return (None, None)

	if current_version.casefold() in ['git head', 'head', 'tip', 'dev', 'devel']:
		_log.debug('[%s] always considered up to date', current_version)
		return (False, None)

	try:
		remote_file = urllib.request.urlopen(url)
	except (urllib.error.URLError, ValueError, OSError, IOError):
		# IOError: socket.error
		_log.exception("cannot retrieve version file from [%s]", url)
		return (None, _('Cannot retrieve version information from:\n\n%s') % url)

	_log.debug('retrieving version information from [%s]', url)

	cfg = gmCfgINI.gmCfgData()
	try:
		#remote_file.read().decode(resource.headers.get_content_charset())
		cfg.add_stream_source(source = 'gm-versions', stream = remote_file, encoding = u'utf8')
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
			msg += '\n'
			msg += _(' New version: "%s"') % latest_release_on_current_branch
			msg += '\n'
			msg += _(' - bug fixes only\n')
			msg += _(' - database fixups may be needed\n')
		if new_release_on_latest_branch_available:
			if current_branch != latest_branch:
				msg += '\n'
				msg += _(' New version: "%s"') % latest_release_on_latest_branch
				msg += '\n'
				msg += _(' - bug fixes and new features\n')
				msg += _(' - database upgrade required\n')
	else:
		msg += '\n'
		msg += _(' New version: "%s"') % latest_release_on_current_branch
		msg += '\n'
		msg += _(' - bug fixes only\n')
		msg += _(' - database fixups may be needed\n')

	msg += '\n\n'
	msg += _(
		'Note, however, that this version may not yet\n'
		'be available *pre-packaged* for your system.'
	)

	msg += '\n\n'
	msg += _('Details are found on <https://www.gnumed.de>.\n')
	msg += '\n'
	msg += _('Version information loaded from:\n\n %s') % url

	return (True, msg)

#===========================================================================
# mail handling
#---------------------------------------------------------------------------
default_mail_sender = 'gnumed@gmx.net'
default_mail_receiver = 'gnumed-devel@gnu.org'
default_mail_server = 'mail.gmx.net'


#---------------------------------------------------------------------------
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.application import MIMEApplication

def compose_email(sender=None, receiver=None, message=None, subject=None, files2attach=None):
	# filenames unicode
	# file content binary or utf8
	# files2attach = [(filename, mimetype-or-None), ...]

	if message is None:
		raise ValueError('<message> is None, cannot compose email')

	message = message.lstrip().lstrip('\r\n').lstrip()

	if sender is None:
		sender = default_mail_sender

	if receiver is None:
		receiver = [default_mail_receiver]

	if subject is None:
		subject = 'compose_email() test'

	if files2attach is None:
		email = MIMEText(message, 'plain', 'utf8')
	else:
		email = MIMEMultipart()
		email.attach(MIMEText(message, 'plain', 'utf8'))

	email['From'] = sender
	email['To'] = ', '.join(receiver)
	email['Subject'] = subject

	if files2attach is None:
		return email

	for file2attach in files2attach:
		filename = file2attach[0]
		try:
			mimetype = file2attach[1]
		except IndexError:
			mimetype = gmMimeLib.guess_mimetype(filename = filename)
		# text/*
		if mimetype.startswith('text/'):
			txt = io.open(filename, mode = 'rt', encoding = 'utf8')
			attachment = MIMEText(txt.read(), 'plain', 'utf8')
			txt.close()
		# image/*
		elif mimetype.startswith('image/'):
			img = io.open(filename, mode = 'rb')
			attachment = MIMEImage(img.read())
			img.close()
		# audio/*
		elif mimetype.startswith('audio/'):
			song = io.open(filename, mode = 'rb')
			attachment = MIMEAudio(song.read())
			song.close()
		# catch-all application/*
		else:
			_log.debug('attaching [%s] with type [%s]', filename, mimetype)
			mime_subtype = mimetype.split('/', 1)[1]
			data = io.open(filename, mode = 'rb')
			attachment = MIMEApplication(data.read(), mime_subtype)
			data.close()

		try:
			attachment.replace_header('Content-Disposition', 'attachment; filename="%s"' % gmTools.fname_from_path(filename))
		except KeyError:
			attachment.add_header('Content-Disposition', 'attachment; filename="%s"' % gmTools.fname_from_path(filename))
		email.attach(attachment)

	return email

#---------------------------------------------------------------------------
def send_email(sender=None, receiver=None, email=None, server=None, auth=None, debug=False):

	if email is None:
		raise ValueError('<email> is None, cannot send')

	if sender is None:
		sender = default_mail_sender

	if receiver is None:
		receiver = [default_mail_receiver]

	if server is None:
		server = default_mail_server

	import smtplib
	failed = False
	refused = []
	try:
		session = smtplib.SMTP(server)
		session.set_debuglevel(debug)
		try:
			session.starttls()
		except smtplib.SMTPException:
			_log.error('cannot enable TLS on [%s]', server)
		session.ehlo()
		if auth is not None:
			session.login(auth['user'], auth['password'])
		refused = session.sendmail(sender, receiver, email.as_string())
		session.quit()
	except smtplib.SMTPException:
		failed = True
		_log.exception('cannot send email')
		gmLog2.log_stack_trace()

	if len(refused) > 0:
		_log.error("refused recipients: %s" % refused)

	if failed:
		return False

	return True

#---------------------------------------------------------------------------
def compose_and_send_email(sender=None, receiver=None, message=None, server=None, auth=None, debug=False, subject=None, attachments=None):
	email = compose_email (
		sender = sender,
		receiver = receiver,
		message = message,
		subject = subject,
		files2attach = attachments
	)
	return send_email (
		sender = sender,
		receiver = receiver,
		email = email,
		server = server,
		auth = auth,
		debug = debug
	)

#===========================================================================
# main
#---------------------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	#-----------------------------------------------------------------------
	def test_compose_email():
		email = compose_email (
			message = 'compose_email() test: üü ßß',
			files2attach = [[sys.argv[2]]]
		)
		print(email.as_string())
		return email

	#-----------------------------------------------------------------------
	def test_send_email():
		email = compose_email (
			message = 'compose_email() test: üü ßß',
			files2attach = [[sys.argv[2]]]
		)
		print(send_email (
#			receiver = u'ncq@localhost',
			email = email,
#			server = 'localhost',
			auth = {'user': default_mail_sender, 'password': 'gnumed-at-gmx-net'},
			debug = True
		))

	#-----------------------------------------------------------------------
	def test_check_for_update():

		test_data = [
			('https://www.gnumed.de/downloads/gnumed-versions.txt', None, None, False),
			('file:///home/ncq/gm-versions.txt', None, None, False),
			('file:///home/ncq/gm-versions.txt', '0.2', '0.2.8.1', False),
			('file:///home/ncq/gm-versions.txt', '0.2', '0.2.8.1', True),
			('file:///home/ncq/gm-versions.txt', '0.2', '0.2.8.5', True)
		]

		for test in test_data:
			print("arguments:", test)
			found, msg = check_for_update(test[0], test[1], test[2], test[3])
			print(msg)

		return
	#-----------------------------------------------------------------------
	def test_dl_data_pack():
		#url = 'file:./x-data_pack.zip'
		#url = 'missing-file.zip'
		url = 'gmTools.py'
		dl_name = download_data_pack(url)
		print(url, "->", dl_name)
		unzip_dir = unzip_data_pack(dl_name)
		print("unzipped into", unzip_dir)

	#-----------------------------------------------------------------------
	def test_browser():
		success = open_url_in_browser(sys.argv[2])
		print(success)
		open_url_in_browser(sys.argv[2], abc=222)

	#-----------------------------------------------------------------------
	def test_mirror_url():
		mirror_url(url = sys.argv[2])

	#-----------------------------------------------------------------------
	#test_check_for_update()
	#test_compose_email()
	#test_send_email()
	#test_dl_data_pack()
	#test_browser()
	test_mirror_url()

#===========================================================================
