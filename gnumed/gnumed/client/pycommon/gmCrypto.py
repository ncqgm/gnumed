# -*- coding: utf-8 -*-

__doc__ = """GNUmed crypto tools.

First and only rule:

	DO NOT REIMPLEMENT ENCRYPTION

	Use existing tools.


Main entry point:

	encrypt_file(filename=None, receiver_key_id=None):
"""
#===========================================================================
__author__ = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

# std libs
import sys
import os
import logging


# GNUmed libs
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLog2
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmTools


_log = logging.getLogger('gm.encryption')

#===========================================================================
# file decryption methods
#---------------------------------------------------------------------------
def gpg_decrypt_file(filename=None, passphrase=None, verbose=False, target_ext=None):
	assert (filename is not None), '<filename> must not be None'

	_log.debug('attempting GPG decryption')
	for cmd in ['gpg2', 'gpg', 'gpg2.exe', 'gpg.exe']:
		found, binary = gmShellAPI.detect_external_binary(binary = cmd)
		if found:
			break
	if not found:
		_log.warning('no gpg binary found')
		return None

	#tmp, fname = os.path.split(filename)
	#basename, tmp = os.path.splitext(fname)
	basename = os.path.splitext(filename)[0]
	filename_decrypted = gmTools.get_unique_filename(prefix = '%s-decrypted-' % basename, suffix = target_ext)
	args = [
		binary,
		'--utf8-strings',
		'--display-charset', 'utf-8',
		'--batch',
		'--no-greeting',
		'--enable-progress-filter',
		'--decrypt',
		'--output', filename_decrypted
		##'--use-embedded-filename'				# not all encrypted files carry a filename
	]
	if verbose:
		args.extend ([
			'--verbose', '--verbose',
			'--debug-level', '8',
			'--debug', 'packet,mpi,crypto,filter,iobuf,memory,cache,memstat,trust,hashing,clock,lookup,extprog'
			##'--debug-all',						# will log passphrase
			##'--debug, 'ipc',						# will log passphrase
			##'--debug-level', 'guru',				# will log passphrase
			##'--debug-level', '9',					# will log passphrase
		])
	args.append(filename)
	success, exit_code, stdout = gmShellAPI.run_process(cmd_line = args, verbose = verbose, encoding = 'utf-8')
	if success:
		return filename_decrypted
	return None

#	args = [binary, '--verbose', '--batch', '--yes', '--passphrase-fd', '0', '--output', filename_decrypted, '--decrypt', filename]
#	_log.debug('GnuPG args: %s' % str(args))
#	try:
#		gpg = subprocess.Popen (
#			args = args,
#			stdin = subprocess.PIPE,
#			stdout = subprocess.PIPE,
#			stderr = subprocess.PIPE,
#			close_fds = False
#		)
#	except (OSError, ValueError, subprocess.CalledProcessError):
#		_log.exception('there was a problem executing gpg')
#		gmDispatcher.send(signal = 'statustext', msg = _('Error running GnuPG. Cannot decrypt data.'), beep = True)
#		return
#	out, error = gpg.communicate(passphrase)
#	_log.debug('gpg returned [%s]', gpg.returncode)
#	if gpg.returncode != 0:
#		_log.debug('GnuPG STDOUT:\n%s', out)
#		_log.debug('GnuPG STDERR:\n%s', error)
#		return None
#
#	return filename_decrypted

#===========================================================================
# file encryption methods
#---------------------------------------------------------------------------
def gpg_encrypt_file_symmetric(filename=None, verbose=False, comment=None):
	assert (filename is not None), '<filename> must not be None'

	_log.debug('attempting symmetric GPG encryption')
	for cmd in ['gpg2', 'gpg', 'gpg2.exe', 'gpg.exe']:
		found, binary = gmShellAPI.detect_external_binary(binary = cmd)
		if found:
			break
	if not found:
		_log.warning('no gpg binary found')
		return None
	filename_encrypted = filename + '.asc'
	args = [
		binary,
		'--utf8-strings',
		'--display-charset', 'utf-8',
		'--batch',
		'--no-greeting',
		'--enable-progress-filter',
		'--symmetric',
		'--cipher-algo', 'AES256',
		'--armor',
		'--output', filename_encrypted
	]
	if comment is not None:
		args.extend(['--comment', comment])
	if verbose:
		args.extend ([
			'--verbose', '--verbose',
			'--debug-level', '8',
			'--debug', 'packet,mpi,crypto,filter,iobuf,memory,cache,memstat,trust,hashing,clock,lookup,extprog',
			##'--debug-all',						# will log passphrase
			##'--debug, 'ipc',						# will log passphrase
			##'--debug-level', 'guru',				# will log passphrase
			##'--debug-level', '9',					# will log passphrase
		])
	args.append(filename)
	success, exit_code, stdout = gmShellAPI.run_process(cmd_line = args, verbose = verbose, encoding = 'utf-8')
	if success:
		return filename_encrypted
	return None

#---------------------------------------------------------------------------
def aes_encrypt_file(filename=None, passphrase=None, verbose=False):
	assert (filename is not None), '<filename> must not be None'
	assert (passphrase is not None), '<passphrase> must not be None'

	if len(passphrase) < 5:
		_log.error('<passphrase> must be at least 5 characters/signs/digits')
		return None

	_log.debug('attempting 7z AES encryption')
	for cmd in ['7z', '7z.exe']:
		found, binary = gmShellAPI.detect_external_binary(binary = cmd)
		if found:
			break
	if not found:
		_log.warning('no 7z binary found, trying gpg')
		return None

	gmLog2.add_word2hide(passphrase)
	filename_encrypted = '%s.7z' % filename
	args = [binary, 'a', '-bb3', '-mx0', "-p%s" % passphrase, filename_encrypted, filename]
	success, exit_code, stdout = gmShellAPI.run_process(cmd_line = args, encoding = 'utf8', verbose = verbose)
	if success:
		return filename_encrypted
	return None

#---------------------------------------------------------------------------
def encrypt_pdf(filename=None, passphrase=None, verbose=False):
	assert (filename is not None), '<filename> must not be None'
	assert (passphrase is not None), '<passphrase> must not be None'

	_log.debug('attempting PDF encryption')
	for cmd in ['qpdf', 'qpdf.exe']:
		found, binary = gmShellAPI.detect_external_binary(binary = cmd)
		if found:
			break
	if not found:
		_log.warning('no qpdf binary found')
		return None

	if len(passphrase) < 5:
		_log.error('<passphrase> must be at least 5 characters/signs/digits')
		return None

	gmLog2.add_word2hide(passphrase)
	filename_encrypted = '%s.encrypted.pdf' % os.path.splitext(filename)[0]
	args = [
		binary,
		'--verbose',
		'--encrypt', passphrase, '', '128',
		'--print=full', '--modify=none', '--extract=n',
		'--use-aes=y',
		'--',
		filename,
		filename_encrypted
	]
	success, exit_code, stdout = gmShellAPI.run_process(cmd_line = args, encoding = 'utf8', verbose = verbose)
	if success:
		return filename_encrypted
	return None

#---------------------------------------------------------------------------
def encrypt_file_symmetric(filename=None, passphrase=None, verbose=False):
	assert (filename is not None), '<filename> must not be None'

	# pdf ?
	enc_filename = encrypt_pdf(filename = filename, passphrase = passphrase, verbose = verbose)
	if enc_filename is not None:
		return enc_filename
	# try GPG based
	enc_filename = gpg_encrypt_file_symmetric(filename = filename, verbose = verbose)
	if enc_filename is not None:
		return enc_filename
	# try 7z based
	return aes_encrypt_file(filename = filename, passphrase = passphrase, verbose = verbose)

#---------------------------------------------------------------------------
def encrypt_file(filename=None, receiver_key_ids=None, passphrase=None, verbose=False):
	assert (filename is not None), '<filename> must not be None'

	# cannot do asymmetric
	if receiver_key_ids is None:
		_log.debug('no receiver key IDs: cannot try asymmetric encryption')
		return encrypt_file_symmetric(filename = filename, passphrase = passphrase, verbose = verbose)

	# asymmetric not implemented yet
	return None

#===========================================================================
# main
#---------------------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	# for testing:
	logging.basicConfig(level = logging.DEBUG)
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	#-----------------------------------------------------------------------
	def test_gpg_decrypt():
		print(gpg_decrypt_file(filename = sys.argv[2], verbose = True))

	#-----------------------------------------------------------------------
	def test_gpg_encrypt_symmetric():
		print(gpg_encrypt_file_symmetric(filename = sys.argv[2], verbose = True, comment = 'GNUmed testing'))

	#-----------------------------------------------------------------------
	def test_aes_encrypt():
		print(aes_encrypt_file(filename = sys.argv[2], passphrase = sys.argv[3], verbose = True))

	#-----------------------------------------------------------------------
	def test_encrypt_pdf():
		print(encrypt_pdf(filename = sys.argv[2], passphrase = sys.argv[3], verbose = True))

	#-----------------------------------------------------------------------
	def test_encrypt_file():
		print(encrypt_file(filename = sys.argv[2], passphrase = sys.argv[3], verbose = True))

	#-----------------------------------------------------------------------
	# encryption
	#test_aes_encrypt()
	#test_encrypt_pdf()
	#test_gpg_encrypt_symmetric()
	test_encrypt_file()

	# decryption
	#test_gpg_decrypt()
