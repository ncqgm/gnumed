# -*- coding: utf-8 -*-

__doc__ = """GNUmed crypto tools.

First and only rule:

	DO NOT REIMPLEMENT ENCRYPTION

	Use existing tools.
"""
#===========================================================================
__author__ = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

# std libs
import sys
import os
import logging
import tempfile


# GNUmed libs
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLog2
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMimeLib


_log = logging.getLogger('gm.encryption')

#===========================================================================
# archiving methods
#---------------------------------------------------------------------------
def create_encrypted_zip_archive_from_dir(source_dir, comment=None, overwrite=True, passphrase=None, verbose=False):
	"""Use 7z to create an encrypted ZIP archive of a directory.

	<source_dir>		will be included into the archive
	<comment>			included as a file containing the comment
	<overwrite>			remove existing archive before creation, avoiding
						*updating* of those, and thereby including unintended data
	<passphrase>		minimum length of 5

	The resulting zip archive will always be named
	"datawrapper.zip" for confidentiality reasons. If callers
	want another name they will have to shutil.move() the zip
	file themselves. This archive will be compressed and
	AES256 encrypted with the given passphrase. Therefore,
	the result will not decrypt with earlier versions of
	unzip software. On Windows, 7z oder WinZip are needed.

	The zip format does not support header encryption thereby
	allowing attackers to gain knowledge of patient details
	by observing the names of files and directories inside
	the encrypted archive.

	To reduce that attack surface, GNUmed will create
	_another_ zip archive inside "datawrapper.zip", which
	eventually wraps up the patient data as "data.zip". That
	archive is not compressed and not encrypted, and can thus
	be unpacked with any old unzipper.

	Note that GNUmed does NOT remember the passphrase for
	you. You will have to take care of that yourself, and
	possibly also safely hand over the passphrase to any
	receivers of the zip archive.
	"""
	if len(passphrase) < 5:
		_log.error('<passphrase> must be at least 5 characters/signs/digits')
		return None
	gmLog2.add_word2hide(passphrase)

	source_dir = os.path.abspath(source_dir)
	if not os.path.isdir(source_dir):
		_log.error('<source_dir> does not exist or is not a directory: %s', source_dir)
		return False

	for cmd in ['7z', '7z.exe']:
		found, binary = gmShellAPI.detect_external_binary(binary = cmd)
		if found:
			break
	if not found:
		_log.warning('no 7z binary found')
		return None

	sandbox_dir = gmTools.mk_sandbox_dir()
	archive_path_inner = os.path.join(sandbox_dir, 'data')
	if not gmTools.mkdir(archive_path_inner):
		_log.error('cannot create scratch space for inner achive: %s', archive_path_inner)
	archive_fname_inner = 'data.zip'
	archive_name_inner = os.path.join(archive_path_inner, archive_fname_inner)
	archive_path_outer = gmTools.gmPaths().tmp_dir
	archive_fname_outer = 'datawrapper.zip'
	archive_name_outer = os.path.join(archive_path_outer, archive_fname_outer)
	# remove existing archives so they don't get *updated* rather than newly created
	if overwrite:
		if not gmTools.remove_file(archive_name_inner, force = True):
			_log.error('cannot remove existing archive [%s]', archive_name_inner)
			return False

		if not gmTools.remove_file(archive_name_outer, force = True):
			_log.error('cannot remove existing archive [%s]', archive_name_outer)
			return False

	# 7z does not support ZIP comments so create a text file holding the comment
	if comment is not None:
		tmp, fname = os.path.split(source_dir.rstrip(os.sep))
		comment_filename = os.path.join(sandbox_dir, '000-%s-comment.txt' % fname)
		with open(comment_filename, mode = 'wt', encoding = 'utf8', errors = 'replace') as comment_file:
			comment_file.write(comment)

	# create inner (data) archive: uncompressed, unencrypted, similar to a tar archive
	args = [
		binary,
		'a',				# create archive
		'-sas',				# be smart about archive name extension
		'-bd',				# no progress indicator
		'-mx0',				# no compression (only store files)
		'-mcu=on',			# UTF8 filenames
		'-l',				# store content of links, not links
		'-scsUTF-8',		# console charset
		'-tzip'				# force ZIP format
	]
	if verbose:
		args.append('-bb3')
		args.append('-bt')
	else:
		args.append('-bb1')
	args.append(archive_name_inner)
	args.append(source_dir)
	if comment is not None:
		args.append(comment_filename)
	success, exit_code, stdout = gmShellAPI.run_process(cmd_line = args, encoding = 'utf8', verbose = verbose)
	if not success:
		_log.error('cannot create inner archive')
		return None

	# create "decompress instructions" file
	instructions_filename = os.path.join(archive_path_inner, '000-on_Windows-open_with-WinZip_or_7z_tools')
	open(instructions_filename, mode = 'wt').close()

	# create outer (wrapper) archive: compressed, encrypted
	args = [
		binary,
		'a',					# create archive
		'-sas',					# be smart about archive name extension
		'-bd',					# no progress indicator
		'-mx9',					# best available zip compression ratio
		'-mcu=on',				# UTF8 filenames
		'-l',					# store content of links, not links
		'-scsUTF-8',			# console charset
		'-tzip',				# force ZIP format
		'-mem=AES256',			# force useful encryption
		'-p%s' % passphrase		# set passphrase
	]
	if verbose:
		args.append('-bb3')
		args.append('-bt')
	else:
		args.append('-bb1')
	args.append(archive_name_outer)
	args.append(archive_path_inner)
	success, exit_code, stdout = gmShellAPI.run_process(cmd_line = args, encoding = 'utf8', verbose = verbose)
	if success:
		return archive_name_outer
	_log.error('cannot create outer archive')
	return None

#---------------------------------------------------------------------------
def create_zip_archive_from_dir(source_dir, archive_name=None, comment=None, overwrite=True, verbose=False):

	source_dir = os.path.abspath(source_dir)
	if not os.path.isdir(source_dir):
		_log.error('<source_dir> does not exist or is not a directory: %s', source_dir)
		return False

	for cmd in ['7z', '7z.exe']:
		found, binary = gmShellAPI.detect_external_binary(binary = cmd)
		if found:
			break
	if not found:
		_log.warning('no 7z binary found')
		return None

	if archive_name is None:
		# do not assume we can write to "sourcedir/../"
		archive_path = gmTools.gmPaths().tmp_dir
		# but do take archive name from source_dir
		tmp, archive_fname = os.path.split(source_dir.rstrip(os.sep) + '.zip')
		archive_name = os.path.join(archive_path, archive_fname)
	# remove any existing archives so they don't get *updated*
	# rather than newly created
	if overwrite:
		if not gmTools.remove_file(archive_name, force = True):
			_log.error('cannot remove existing archive [%s]', archive_name)
			return False
	# 7z does not support ZIP comments so create
	# a text file holding the comment ...
	if comment is not None:
		comment_filename = os.path.abspath(archive_name) + '.comment.txt'
		if gmTools.remove_file(comment_filename, force = True):
			with open(comment_filename, mode = 'wt', encoding = 'utf8', errors = 'replace') as comment_file:
				comment_file.write(comment)
		else:
			_log.error('cannot remove existing archive comment file [%s]', comment_filename)
			comment = None

	# compress
	args = [
		binary,
		'a',				# create archive
		'-sas',				# be smart about archive name extension
		'-bd',				# no progress indicator
		'-mx9',				# best available zip compression ratio
		'-mcu=on',			# UTF8 filenames
		'-l',				# store content of links, not links
		'-scsUTF-8',		# console charset
		'-tzip'				# force ZIP format
	]
	if verbose:
		args.append('-bb3')
		args.append('-bt')
	else:
		args.append('-bb1')
	args.append(archive_name)
	args.append(source_dir)
	if comment is not None:
		args.append(comment_filename)
	success, exit_code, stdout = gmShellAPI.run_process(cmd_line = args, encoding = 'utf8', verbose = verbose)
	if comment is not None:
		gmTools.remove_file(comment_filename)
	if success:
		return archive_name

	return None

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

#===========================================================================
# file encryption methods
#---------------------------------------------------------------------------
def gpg_encrypt_file_symmetric(filename=None, comment=None, verbose=False, passphrase=None, remove_unencrypted=False):

	#add short decr instr to comment
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
	pwd_fname = None
	if passphrase is not None:
		pwd_file = tempfile.NamedTemporaryFile(mode = 'w+t', encoding = 'utf8', delete = False)
		pwd_fname = pwd_file.name
		args.extend ([
			'--pinentry-mode', 'loopback',
			'--passphrase-file', pwd_fname
		])
		pwd_file.write(passphrase)
		pwd_file.close()
	args.append(filename)
	try:
		success, exit_code, stdout = gmShellAPI.run_process(cmd_line = args, verbose = verbose, encoding = 'utf-8')
	finally:
		if pwd_fname is not None:
			os.remove(pwd_fname)
	if not success:
		return None
	if not remove_unencrypted:
		return filename_encrypted
	if gmTools.remove_file(filename):
		return filename_encrypted
	gmTools.remove_file(filename_encrypted)
	return None

#---------------------------------------------------------------------------
def aes_encrypt_file(filename=None, passphrase=None, comment=None, verbose=False, remove_unencrypted=False):
	assert (filename is not None), '<filename> must not be None'
	assert (passphrase is not None), '<passphrase> must not be None'

	if len(passphrase) < 5:
		_log.error('<passphrase> must be at least 5 characters/signs/digits')
		return None
	gmLog2.add_word2hide(passphrase)

	#add 7z/winzip url to comment.txt
	_log.debug('attempting 7z AES encryption')
	for cmd in ['7z', '7z.exe']:
		found, binary = gmShellAPI.detect_external_binary(binary = cmd)
		if found:
			break
	if not found:
		_log.warning('no 7z binary found, trying gpg')
		return None

	if comment is not None:
		archive_path, archive_name = os.path.split(os.path.abspath(filename))
		comment_filename = gmTools.get_unique_filename (
			prefix = '%s.7z.comment-' % archive_name,
			tmp_dir = archive_path,
			suffix = '.txt'
		)
		with open(comment_filename, mode = 'wt', encoding = 'utf8', errors = 'replace') as comment_file:
			comment_file.write(comment)
	else:
		comment_filename = ''
	filename_encrypted = '%s.7z' % filename
	args = [binary, 'a', '-bb3', '-mx0', "-p%s" % passphrase, filename_encrypted, filename, comment_filename]
	encrypted, exit_code, stdout = gmShellAPI.run_process(cmd_line = args, encoding = 'utf8', verbose = verbose)
	gmTools.remove_file(comment_filename)
	if not encrypted:
		return None
	if not remove_unencrypted:
		return filename_encrypted
	if gmTools.remove_file(filename):
		return filename_encrypted
	gmTools.remove_file(filename_encrypted)
	return None

#---------------------------------------------------------------------------
def encrypt_pdf(filename=None, passphrase=None, verbose=False, remove_unencrypted=False):
	assert (filename is not None), '<filename> must not be None'
	assert (passphrase is not None), '<passphrase> must not be None'

	if len(passphrase) < 5:
		_log.error('<passphrase> must be at least 5 characters/signs/digits')
		return None

	gmLog2.add_word2hide(passphrase)
	_log.debug('attempting PDF encryption')
	for cmd in ['qpdf', 'qpdf.exe']:
		found, binary = gmShellAPI.detect_external_binary(binary = cmd)
		if found:
			break
	if not found:
		_log.warning('no qpdf binary found')
		return None

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
	if not success:
		return None

	if not remove_unencrypted:
		return filename_encrypted

	if gmTools.remove_file(filename):
		return filename_encrypted

	gmTools.remove_file(filename_encrypted)
	return None

#---------------------------------------------------------------------------
def encrypt_file_symmetric(filename=None, passphrase=None, comment=None, verbose=False, remove_unencrypted=False, convert2pdf=False):
	"""Encrypt <filename> with a symmetric cipher.

	<convert2pdf> - True: convert <filename> to PDF, if possible, and encrypt that.
	"""
	assert (filename is not None), '<filename> must not be None'

	if convert2pdf:
		_log.debug('PDF encryption preferred, attempting conversion if needed')
		pdf_fname = gmMimeLib.convert_file (
			filename = filename,
			target_mime = 'application/pdf',
			target_filename = filename + '.pdf',
			verbose = verbose
		)
		if pdf_fname is not None:
			_log.debug('successfully converted to PDF')
			# remove non-pdf file
			gmTools.remove_file(filename)
			filename = pdf_fname

	# try PDF-inherent AES
	encrypted_filename = encrypt_pdf (
		filename = filename,
		passphrase = passphrase,
		verbose = verbose,
		remove_unencrypted = remove_unencrypted
	)
	if encrypted_filename is not None:
		return encrypted_filename

	# try 7z based AES
	encrypted_filename = aes_encrypt_file (
		filename = filename,
		passphrase = passphrase,
		comment = comment,
		verbose = verbose,
		remove_unencrypted = remove_unencrypted
	)
	if encrypted_filename is not None:
		return encrypted_filename

	# try GPG based AES
	return gpg_encrypt_file_symmetric(filename = filename, passphrase = passphrase, comment = comment, verbose = verbose, remove_unencrypted = remove_unencrypted)

#---------------------------------------------------------------------------
def encrypt_file(filename=None, receiver_key_ids=None, passphrase=None, comment=None, verbose=False, remove_unencrypted=False, convert2pdf=False):
	"""Encrypt an arbitrary file.

	<remove_unencrypted>
		True: remove unencrypted source file if encryption succeeded
	<convert2pdf>
		True: attempt conversion to PDF of input file before encryption
			success: the PDF is encrypted (and the non-PDF source file is removed)
			failure: the source file is encrypted
	"""
	assert (filename is not None), '<filename> must not be None'

	# cannot do asymmetric
	if receiver_key_ids is None:
		_log.debug('no receiver key IDs: cannot try asymmetric encryption')
		return encrypt_file_symmetric (
			filename = filename,
			passphrase = passphrase,
			comment = comment,
			verbose = verbose,
			remove_unencrypted = remove_unencrypted,
			convert2pdf = convert2pdf
		)

	# asymmetric not implemented yet
	return None

#---------------------------------------------------------------------------
def encrypt_directory_content(directory=None, receiver_key_ids=None, passphrase=None, comment=None, verbose=False, remove_unencrypted=True, convert2pdf=False):
	assert (directory is not None), 'source <directory> must not be None'
	_log.debug('encrypting content of [%s]', directory)
	try:
		items = os.listdir(directory)
	except OSError:
		return False

	for item in items:
		full_item = os.path.join(directory, item)
		if os.path.isdir(full_item):
			subdir_encrypted = encrypt_directory_content (
				directory = full_item,
				receiver_key_ids = receiver_key_ids,
				passphrase = passphrase,
				comment = comment,
				verbose = verbose
			)
			if subdir_encrypted is False:
				return False
			continue

		fname_encrypted = encrypt_file (
			filename = full_item,
			receiver_key_ids = receiver_key_ids,
			passphrase = passphrase,
			comment = comment,
			verbose = verbose,
			remove_unencrypted = remove_unencrypted,
			convert2pdf = convert2pdf
		)
		if fname_encrypted is None:
			return False

	return True

#---------------------------------------------------------------------------
def pdf_is_encrypted(filename:str=None) -> bool:
	pass

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
		print(gpg_encrypt_file_symmetric(filename = sys.argv[2], passphrase = sys.argv[3], verbose = True, comment = 'GNUmed testing'))

	#-----------------------------------------------------------------------
	def test_aes_encrypt():
		print(aes_encrypt_file(filename = sys.argv[2], passphrase = sys.argv[3], comment = sys.argv[4], verbose = True))

	#-----------------------------------------------------------------------
	def test_encrypt_pdf():
		print(encrypt_pdf(filename = sys.argv[2], passphrase = sys.argv[3], verbose = True))

	#-----------------------------------------------------------------------
	def test_encrypt_file():
		print(encrypt_file(filename = sys.argv[2], passphrase = sys.argv[3], verbose = True, convert2pdf = True))

	#-----------------------------------------------------------------------
	def test_zip_archive_from_dir():
		print(create_zip_archive_from_dir (
			sys.argv[2],
			#archive_name=None,
			comment = 'GNUmed test archive',
			overwrite = True,
			verbose = True
		))

	#-----------------------------------------------------------------------
	def test_encrypted_zip_archive_from_dir():
		print(create_encrypted_zip_archive_from_dir (
			sys.argv[2],
			comment = 'GNUmed test archive',
			overwrite = True,
			passphrase = sys.argv[3],
			verbose = True
		))

	#-----------------------------------------------------------------------
	# encryption
	#test_aes_encrypt()
	#test_encrypt_pdf()
	#test_gpg_encrypt_symmetric()
	test_encrypt_file()

	# decryption
	#test_gpg_decrypt()

	#test_zip_archive_from_dir()
	#test_encrypted_zip_archive_from_dir()
