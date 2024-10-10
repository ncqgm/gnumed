# -*- coding: utf-8 -*-

"""GNUmed crypto tools.

First and only rule:

	DO NOT REIMPLEMENT ENCRYPTION

	Use existing tools.
"""
#===========================================================================
__author__ = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

# std libs
import sys
import os
import logging
import tempfile
import shutil


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
def create_encrypted_zip_archive_from_dir(source_dir:str, comment:str=None, overwrite:bool=True, passphrase:str=None, verbose:bool=False) -> str:
	"""Create encrypted archive of a directory.

	The encrypted archive file will always be named

		gmTools.gmPaths().tmp_dir/datawrapper.zip

	for confidentiality reasons. If callers want another name
	they will have to shutil.move() the zip file themselves.
	This archive will be compressed and AES256 encrypted with
	the given passphrase. Therefore, the result will not
	decrypt with earlier versions of unzip software. On
	Windows, 7z oder WinZip are needed.

	The zip format does not support header encryption thereby
	allowing attackers to gain knowledge of patient details
	by observing the names of files and directories inside
	the encrypted archive. To reduce that attack surface,
	GNUmed will create _another_ zip archive inside
	"datawrapper.zip", which eventually wraps up the patient
	data as "data.zip". That archive is not compressed and
	not encrypted, and can thus be unpacked with any old
	unzipper.

	Note that GNUmed does NOT remember the passphrase for
	you. You will have to take care of that yourself, and
	possibly also safely hand over the passphrase to any
	receivers of the zip archive.

	Args:
		source_dir: the directory to archive and encrypt
		comment: included as a file containing the comment
		overwrite: remove preexisting archive before creation, avoiding *updating* of same, and thereby including unintended data
		passphrase: minimum length of 5 if given

	Returns:
		Archive path (always gmTools.gmPaths().tmp_dir/datawrapper.zip) or None.
	"""
	assert (source_dir is not None), '<source_dir> must not be <None>'
	if len(passphrase) < 5:
		_log.error('<passphrase> must be at least 5 characters/signs/digits')
		return None

	gmLog2.add_word2hide(passphrase)
	source_dir = os.path.abspath(source_dir)
	if not os.path.isdir(source_dir):
		_log.error('<source_dir> does not exist or is not a directory: %s', source_dir)
		return None

	for cmd in ['7z', '7z.exe']:
		found, binary = gmShellAPI.detect_external_binary(binary = cmd)
		if found:
			break
	if not found:
		_log.warning('no 7z binary found')
		return None

	_log.debug('source directory: %s', source_dir)
	archive_sandbox = gmTools.mk_sandbox_dir()
	_log.debug('archive creation sandbox: %s', archive_sandbox)
	inner_archive_dir = os.path.join(archive_sandbox, 'inner')
	if not gmTools.mkdir(inner_archive_dir):
		_log.error('cannot create scratch space for inner archive: %s', inner_archive_dir)
		return None

	outer_archive_dir = os.path.join(archive_sandbox, 'outer')
	if not gmTools.mkdir(outer_archive_dir):
		_log.error('cannot create scratch space for outer archive: %s', outer_archive_dir)
		return None

	inner_archive_name = os.path.join(inner_archive_dir, 'data.zip')
	outer_archive_name = os.path.join(outer_archive_dir, 'datawrapper.zip')
	# remove existing archives so they don't get *updated* rather than newly created
	if overwrite:
		if not gmTools.remove_file(inner_archive_name, force = True):
			_log.error('cannot remove existing archive [%s]', inner_archive_name)
			return None

		if not gmTools.remove_file(outer_archive_name, force = True):
			_log.error('cannot remove existing archive [%s]', outer_archive_name)
			return None

	tmp = gmTools.copy_tree_content(source_dir, inner_archive_dir)
	if not tmp:
		_log.error('cannot move source data to inner archive creation scratch dir')
		return None

	# 7z does not support ZIP comments so create a text file holding the comment
	if comment is not None:
		tmp, fname = os.path.split(source_dir.rstrip(os.sep))
		comment_filename = os.path.join(inner_archive_dir, '000-%s-comment.txt' % fname)
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
		# now the default and switch not supported anymore
		#'-l',				# store content of links, not links
		'-scsUTF-8',		# console charset
		'-tzip'				# force ZIP format
	]
	if verbose:
		args.append('-bb3')
		args.append('-bt')
	else:
		args.append('-bb1')
	args.append(inner_archive_name)
	args.append(os.path.join(inner_archive_dir, '.'))
	_log.debug(args)
	old_cwd = os.getcwd()
	os.chdir(inner_archive_dir)
	success, exit_code, stdout = gmShellAPI.run_process(cmd_line = args, encoding = 'utf8', verbose = verbose)
	os.chdir(old_cwd)
	if not success:
		_log.error('cannot create inner archive')
		return None

	# test
	args = [
		binary,
		't',				# test archive
		'-bd',				# no progress indicator
		'-scsUTF-8'			# console charset
	]
	if verbose:
		args.append('-bb3')
		args.append('-bt')
	else:
		args.append('-bb1')
	args.append(inner_archive_name)
	_log.debug(args)
	success, exit_code, stdout = gmShellAPI.run_process(cmd_line = args, encoding = 'utf8', verbose = verbose)
	if not success:
		_log.error('cannot verify integrity of inner zip archive')
		return None

	# FIXME: needs error handling
	shutil.move(inner_archive_name, outer_archive_dir)
	# create "decompress instructions" file
	instructions_filename = os.path.join(outer_archive_dir, '000-on_Windows-open_with-WinZip_or_7z_tools')
	open(instructions_filename, mode = 'wt').close()
	# create outer (wrapper) archive: compressed, encrypted
	args = [
		binary,
		'a',					# create archive
		'-sas',					# be smart about archive name extension
		'-bd',					# no progress indicator
		'-mx9',					# best available zip compression ratio
		'-mcu=on',				# UTF8 filenames
		# now the default and switch not supported anymore
		#'-l',					# store content of links, not links
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
	args.append(outer_archive_name)
	args.append(os.path.join(outer_archive_dir, '.'))
	_log.debug(args)
	old_cwd = os.getcwd()
	os.chdir(outer_archive_dir)
	success, exit_code, stdout = gmShellAPI.run_process(cmd_line = args, encoding = 'utf8', verbose = verbose)
	os.chdir(old_cwd)
	if not success:
		_log.error('cannot create wrapper archive')
		return None

	# test
	args = [
		binary,
		't',					# test archive
		'-bd',					# no progress indicator
		'-scsUTF-8',			# console charset
		'-p%s' % passphrase		# set passphrase
	]
	if verbose:
		args.append('-bb3')
		args.append('-bt')
	else:
		args.append('-bb1')
	args.append(outer_archive_name)
	_log.debug(args)
	success, exit_code, stdout = gmShellAPI.run_process(cmd_line = args, encoding = 'utf8', verbose = verbose)
	if not success:
		_log.error('cannot verify integrity of outer zip archive')
		return None

	return outer_archive_name

#---------------------------------------------------------------------------
def create_zip_archive_from_dir(source_dir:str, archive_name:str=None, comment:str=None, overwrite:bool=True, verbose:bool=False) -> str:
	"""Create archive of a directory.

	Args:
		source_dir: the directory to archive and encrypt
		archive_name: name of resulting zip archive
		comment: included as a file containing the comment
		overwrite: remove preexisting archive before creation, avoiding *updating* of same, and thereby including unintended data

	Returns:
		Archive path or None.
	"""
	assert (source_dir is not None), '<source_dir> must not be <None>'
	source_dir = os.path.abspath(source_dir)
	if not os.path.isdir(source_dir):
		_log.error('<source_dir> does not exist or is not a directory: %s', source_dir)
		return None

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
			return None
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
		# now the default and switch not supported anymore:
		#'-l',				# store content of links, not links
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
	_log.debug(args)
	success, exit_code, stdout = gmShellAPI.run_process(cmd_line = args, encoding = 'utf8', verbose = verbose)
	if comment is not None:
		gmTools.remove_file(comment_filename)
	if not success:
		_log.error('cannot create zip archive')
		return None

	# test
	args = [
		binary,
		't',				# test archive
		'-bd',				# no progress indicator
		'-scsUTF-8'			# console charset
	]
	if verbose:
		args.append('-bb3')
		args.append('-bt')
	else:
		args.append('-bb1')
	args.append(archive_name)
	_log.debug(args)
	success, exit_code, stdout = gmShellAPI.run_process(cmd_line = args, encoding = 'utf8', verbose = verbose)
	if not success:
		_log.error('cannot verify zip archive integrity')
		return None

	return archive_name

#===========================================================================
# file decryption methods
#---------------------------------------------------------------------------
def gpg_decrypt_file(filename=None, verbose=False, target_ext=None):
	"""The system is expected to be set up for safely getting the
	   passphrase from the user, typically via gpg-agent.
	"""
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

#---------------------------------------------------------------------------
def decrypt_pdf(filename:str=None, passphrase:str=None, verbose:bool=False) -> str:
	assert (filename is not None), '<filename> must not be None'
	assert (passphrase is not None), '<passphrase> must not be None'

	gmLog2.add_word2hide(passphrase)
	_log.debug('attempting PDF decryption')
	for cmd in ['qpdf', 'qpdf.exe']:
		found, binary = gmShellAPI.detect_external_binary(binary = cmd)
		if found:
			break
	if not found:
		_log.warning('no qpdf binary found')
		return None

	filename_decrypted = '%s.decrypted.pdf' % os.path.splitext(filename)[0]
	args = [
		binary,
		'--verbose',
		'--password-mode=unicode',
		'--decrypt',
		'--password=%s' % passphrase,
		'--',
		filename,
		filename_decrypted
	]
	success, exit_code, stdout = gmShellAPI.run_process (
		cmd_line = args,
		encoding = 'utf8',
		verbose = verbose,
		acceptable_return_codes = [0, 3]
	)
	if not success:
		return None

	return filename_decrypted

#===========================================================================
# file encryption methods
#---------------------------------------------------------------------------
def encrypt_file_symmetric_gpg(filename=None, comment=None, verbose=False, passphrase=None, remove_unencrypted=False) -> str:
	"""Encrypt file symmetrically with GPG.

	Args:
		filename: the file to encrypt
		passphrase: minimum of 5 characters if given
		comment: a comment on the file to be put into a sidecar file, will also be encrypted
		remove_unencrypted: remove unencrypted source file if encryption succeeded

	Returns:
		Name of encrypted file or None.
	"""
	#add short decr instr to comment
	assert (filename is not None), '<filename> must not be None'
	if passphrase is not None:
		if len(passphrase) < 5:
			_log.error('<passphrase> must be at least 5 characters/signs/digits')
			return None

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
def encrypt_file_symmetric_7z(filename:str=None, passphrase:str=None, comment:str=None, verbose:bool=False, remove_unencrypted:bool=False) -> str:
	"""Encrypt a file symmetrically with 7zip.

	Args:
		filename: the file to encrypt
		passphrase: minimum of 5 characters
		comment: a comment on the file to be put into a sidecar file, will also be encrypted
		remove_unencrypted: remove unencrypted source file if encryption succeeded

	Returns:
		Name of encrypted file or None.
	"""
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
def encrypt_pdf(filename:str=None, passphrase:str=None, verbose:bool=False, remove_unencrypted:bool=False) -> str:
	"""Encrypt a PDF file per spec (AES, that is).

	Args:
		filename: PDF file to encrypt
		passphrase: minimum of 5 characters
		remove_unencrypted: remove unencrypted source file if encryption succeeds

	Returns:
		Name of encrypted PDF or None.
	"""
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
		'--password-mode=unicode',
		'--encrypt', passphrase, '', '128',
		'--print=full', '--modify=none', '--extract=n',
		'--use-aes=y',
		'--',
		filename,
		filename_encrypted
	]
	_log.debug(args)
	success, exit_code, stdout = gmShellAPI.run_process (
		cmd_line = args,
		encoding = 'utf8',
		verbose = verbose,
		acceptable_return_codes = [0, 3]
	)
	if not success:
		return None

	if not remove_unencrypted:
		return filename_encrypted

	if gmTools.remove_file(filename):
		return filename_encrypted

	gmTools.remove_file(filename_encrypted)
	return None

#---------------------------------------------------------------------------
def encrypt_file_symmetric(filename:str=None, passphrase:str=None, comment:str=None, verbose:bool=False, remove_unencrypted:bool=False, convert2pdf:bool=False) -> str:
	"""Encrypt file with a symmetric cipher.

	Args:
		filename: file to encrypt
		passphrase: minimum of 5 characters
		remove_unencrypted: remove unencrypted source file if encryption succeeded
		comment: a comment to be included within the encrypted output
		remove_unencrypted: remove unencrypted source file if encryption succeeds
		convert2pdf: attempt converting _filename_ to PDF and encrypt that on success

	Returns:
		Name of encrypted PDF or None.
	"""
	assert (filename is not None), '<filename> must not be None'

	if passphrase is None:
		# try GPG based AES only, as GPG is the only supported method
		# for securely getting a passphrase from the user
		return encrypt_file_symmetric_gpg (
			filename = filename,
			passphrase = None,
			comment = comment,
			verbose = verbose,
			remove_unencrypted = remove_unencrypted
		)

	# else try other methods, too
	if len(passphrase) < 5:
		_log.error('<passphrase> must be at least 5 characters/signs/digits')
		return None

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
			if remove_unencrypted:
				# remove non-pdf file
				gmTools.remove_file(filename)
			filename = pdf_fname

	# try PDF-based encryption
	encrypted_filename = encrypt_pdf (
		filename = filename,
		passphrase = passphrase,
		verbose = verbose,
		remove_unencrypted = remove_unencrypted
	)
	if encrypted_filename is not None:
		return encrypted_filename

	# try 7z based encryption
	encrypted_filename = encrypt_file_symmetric_7z (
		filename = filename,
		passphrase = passphrase,
		comment = comment,
		verbose = verbose,
		remove_unencrypted = remove_unencrypted
	)
	if encrypted_filename is not None:
		return encrypted_filename

	# try GPG based encryption
	return encrypt_file_symmetric_gpg (
		filename = filename,
		passphrase = passphrase,
		comment = comment,
		verbose = verbose,
		remove_unencrypted = remove_unencrypted
	)

#---------------------------------------------------------------------------
def encrypt_file(filename:str=None, receiver_key_ids:list=None, passphrase:str=None, comment:str=None, verbose:bool=False, remove_unencrypted:bool=False, convert2pdf:bool=False) -> str:
	"""Encrypt an arbitrary file, symmetrically or asymmetrically.

	Asymmetric encryption will only be attempted if receiver_key_ids are given.

	Args:
		filename: file to encrypt
		receiver_key_ids: list of public key ids of receivers, only relevant for asymmetric encryption
		passphrase: minimum of 5 characters if given/needed
		comment: a comment to be included within the encrypted output
		remove_unencrypted: remove unencrypted source file if encryption succeeds
		convert2pdf: _attempt_ conversion of input file to PDF before encryption
			- success: the PDF is encrypted (and the non-PDF source file is removed)
			- failure: the source file is encrypted

	Returns:
		Name of encrypted file or None.
	"""
	assert (filename is not None), '<filename> must not be None'
	if receiver_key_ids is None:
		# cannot do asymmetric
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
	_log.error('asymmetric encryption not implemented')
	return None

#---------------------------------------------------------------------------
def encrypt_directory_content(directory:str=None, receiver_key_ids:list=None, passphrase:str=None, comment:str=None, verbose:bool=False, remove_unencrypted:bool=True, convert2pdf:bool=False, store_passphrase_cb=None, passphrase_password:str=None) -> bool:
	"""Encrypt the content of a directory, file by file, symmetrically or asymmetrically.

	Asymmetric encryption will only be attempted if receiver_key_ids are given.

	Args:
		directory: directory from which to encrypt files
		receiver_key_ids: list of public key ids of receivers, only relevant for asymmetric encryption
		passphrase: minimum of 5 characters if given/needed
		comment: a comment to be included within the encrypted output
		remove_unencrypted: remove unencrypted source file if encryption succeeds
		convert2pdf: _attempt_ conversion of input file to PDF before encryption
			- success: the PDF is encrypted (and the non-PDF source file is removed)
			- failure: the source file is encrypted
		store_passphrase_cb: function to call to store passphrases for encrypted files (filename, passphrase, comment)
		passphrase_password: password to symmetrically encrypt passphrase for safekeeping in GNUmed if not pubkeys available

	Returns:
		True (success) or False.
	"""

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

		store_passphrase_cb(filename = fname_encrypted, passphrase = passphrase, comment = comment, symmetric_password = passphrase_password)
	return True

#---------------------------------------------------------------------------
def is_encrypted_pdf(filename:str=None, verbose:bool=False) -> bool:
	"""Check encryption status of PDF.

	Requires qpdf to be installed.

	Returns:
		True/False/None: None -- unknown or not PDF
	"""
	assert (filename is not None), '<filename> must not be None'

	mimetype = gmMimeLib.guess_mimetype(filename = filename)
	if mimetype != 'application/pdf':
		_log.info('not a PDF')
		return None

	_log.debug('checking PDF encryption')
	for cmd in ['qpdf', 'qpdf.exe']:
		found, binary = gmShellAPI.detect_external_binary(binary = cmd)
		if found:
			break
	if not found:
		_log.warning('no qpdf binary found')
		return None

	args = [
		binary,
		'--verbose',
		'--is-encrypted',
		'--',
		filename
	]
	success, exit_code, stdout = gmShellAPI.run_process (
		cmd_line = args,
		encoding = 'utf8',
		verbose = verbose,
		acceptable_return_codes = [0, 2]
	)
	if not success:
		return None

	if exit_code == 0:
		return True

	if exit_code == 2:
		return False

	return None

#===========================================================================
def encrypt_data_with_7z(data, passphrase:str=None, verbose:bool=False) -> str:
	"""Encrypt input data symmetrically with 7zip.

	Args:
		data: the data to encrypt
		passphrase: minimum of 5 characters

	Returns:
		Encrypted data or None.
	"""
	assert data, '<data> must be defined'
	assert passphrase, '<passphrase> must be defined'

	if len(passphrase) < 5:
		_log.error('<passphrase> must be at least 5 characters/signs/digits')
		return None

	gmLog2.add_word2hide(passphrase)
	_log.debug('attempting 7z AES encryption')
	for cmd in ['7z', '7z.exe']:
		found, binary = gmShellAPI.detect_external_binary(binary = cmd)
		if found:
			break
	if not found:
		_log.warning('no 7z binary found')
		return None

	args = [
		binary,
		'a',		# create archive
		'-si',		# read data from STDIN
		'-so',		# write to STDOUT
		'-bd',		# no progress indicator
		'-mx0',		# compression level
		'-an',		# do not parse archive name
		'-tgzip',	# force data type to gzip (for streaming)
		"-p%s" % passphrase
	]
	if verbose:
		args.append('-bb3')		# log level
		args.append('-bt')		# timings
	if isinstance(data, str):
		encoding = 'utf-8'
	else:
		encoding = None
	encrypted, exit_code, stdout = gmShellAPI.run_process (
		cmd_line = args,
		input_data = data,
		encoding = encoding,
		verbose = verbose
	)
	if not encrypted:
		return None

	return stdout

#---------------------------------------------------------------------------
def encrypt_data_with_gpg_symmetrically(data, passphrase:str=None, comment:str=None, verbose:bool=False) -> str:
	"""Encrypt input data symmetrically with gpg.

	Args:
		data: the data to encrypt
		passphrase: minimum of 5 characters
		comment: a comment to be attached to the (ASCII-armored) encrypted output

	Returns:
		ASCII-armored encrypted data or None on failure.
	"""
	assert data, '<data> must be defined'
	assert passphrase, '<passphrase> must be defined'

	if len(passphrase) < 5:
		_log.error('<passphrase> must be at least 5 characters/signs/digits')
		return None

	gmLog2.add_word2hide(passphrase)
	_log.debug('attempting GPG AES encryption')
	for cmd in ['gpg2', 'gpg', 'gpg2.exe', 'gpg.exe']:
		found, binary = gmShellAPI.detect_external_binary(binary = cmd)
		if found:
			break
	if not found:
		_log.warning('no gpg binary found')
		return None

	gpg = [
		binary,
		'--utf8-strings',
		'--display-charset', 'utf-8',
		'--symmetric',					# encrypt
		'--cipher-algo', 'AES256',
		'--armor',
		'--no-greeting',
		'--no-tty',						# there simply IS no TTY
		'--batch',						# required by passphrase file
		'--pinentry-mode', 'loopback'	# required by passphrase file

	]
	if comment and comment.strip():
		gpg.extend(['--comment', comment.strip()])
	if verbose:
		gpg.extend ([
			'--verbose', '--verbose',
			'--debug-level', '8',
			'--debug', 'packet,mpi,crypto,filter,iobuf,memory,cache,memstat,trust,hashing,clock,lookup,extprog',
			##'--debug-all',						# will log passphrase
			##'--debug, 'ipc',						# will log passphrase
			##'--debug-level', 'guru',				# will log passphrase
			##'--debug-level', '9',					# will log passphrase
		])
	if isinstance(data, str):
		encoding = 'utf-8'
	else:
		encoding = None
	pwd_file = tempfile.NamedTemporaryFile(mode = 'w+t', encoding = 'utf8', delete = False)
	pwd_fname = pwd_file.name
	gpg.append('--passphrase-file')
	gpg.append(pwd_fname)
	pwd_file.write(passphrase)
	pwd_file.close()
	success, exit_code, stdout = gmShellAPI.run_process (
		cmd_line = gpg,
		input_data = data,
		verbose = verbose,
		encoding = encoding
	)
	if not success:
		return None

	return stdout

#---------------------------------------------------------------------------
def encrypt_data_with_gpg(data, recipient_key_files:list[str], comment:str=None, verbose:bool=False) -> str:
	"""Encrypt data with public key(s).

	Requires GPG to be installed.

	Args:
		data: data to be encrypted, assumed to be UTF-8 if a string, otherwise treated as binary
		recipient_key_files: files with public keys to encrypt to
		comment: a comment to be attached to the (ASCII-armored) encrypted output

	Returns:
		ASCII-armored encrypted data or None on failure.
	"""
	assert data, '<data> must be passed in'
	assert recipient_key_files, '<recipient_key_files> must be passed in'

	for cmd in ['gpg2', 'gpg', 'gpg2.exe', 'gpg.exe']:
		found, binary = gmShellAPI.detect_external_binary(binary = cmd)
		if found:
			break
	if not found:
		_log.warning('no gpg binary found')
		return None

	gpg = [
		binary,
		'--utf8-strings',
		'--display-charset', 'utf-8',
		'--encrypt',
		'--armor',
		'--no-greeting',
		'--no-tty',						# there simply IS no TTY
		'--batch'						# no interaction with user
	]
	for pk_file in recipient_key_files:
		gpg.extend(['--recipient-file', pk_file])
	if comment and comment.strip():
		gpg.extend(['--comment', comment.strip()])
	if verbose:
		gpg.extend ([
			'--verbose', '--verbose',
			'--debug-level', '8',
			'--debug', 'packet,mpi,crypto,filter,iobuf,memory,cache,memstat,trust,hashing,clock,lookup,extprog',
			##'--debug-all',						# will log passphrase
			##'--debug, 'ipc',						# will log passphrase
			##'--debug-level', 'guru',				# will log passphrase
			##'--debug-level', '9',					# will log passphrase
		])
	if isinstance(data, str):
		encoding = 'utf-8'
	else:
		encoding = None
	success, exit_code, stdout = gmShellAPI.run_process (
		cmd_line = gpg,
		input_data = data,
		verbose = verbose,
		encoding = encoding
	)
	if not success:
		return None

	return stdout

#===========================================================================
def encrypt_data(data, recipient_key_files:list[str], comment:str=None, verbose:bool=False, retry_symmetric:bool=False, symmetric_password:str=None) -> dict[str, str] | None:
	"""Encrypt data.

	Args:
		data: data to be encrypted, assumed to be UTF-8 if a string, otherwise treated as binary
		recipient_key_files: files with public keys to encrypt to
		comment: a comment to attach to the encrypted data, if possible
		retry_symmetric: try symmetric if asymmetric fails despite having recipients
		symmetric_password: if there is no recipients defined by public key use this key to *symmetrically* encrypt

	Returns:
		a dictionary {'data': the encrypted data, 'method': a tag defining the method used} or None
	"""
	assert recipient_key_files or symmetric_password, 'either <recipient_key_files> or <symmetric_password> must be defined'

	if recipient_key_files:
		enc_data = encrypt_data_with_gpg (
			data = data,
			recipient_key_files = recipient_key_files,
			comment = comment,
			verbose = verbose
		)
		if enc_data:
			return {'data': enc_data, 'method': 'gpg::asymmetric'}

		_log.error('cannot asymmetrically encrypt data')
		if not retry_symmetric:
			return None

	if not symmetric_password:
		_log.error('cannot symmetrically encrypt data')
		return None

	enc_data = encrypt_data_with_gpg_symmetrically (
		data = data,
		comment = comment,
		passphrase = symmetric_password,
		verbose = verbose
	)
	if enc_data:
		return {'data': enc_data, 'method': 'gpg::symmetric'}

	enc_data = encrypt_data_with_7z (
		data,
		passphrase = symmetric_password,
		verbose = verbose
	)
	if enc_data:
		return {'data': enc_data, 'method': '7z::symmetric::gzip'}

	return None

#===========================================================================
# file anonymization methods
#---------------------------------------------------------------------------
def anonymize_file(filename):
	assert (filename is not None), '<filename> must not be None'

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

	gmLog2.print_logfile_name()

	#-----------------------------------------------------------------------
	def test_gpg_decrypt():
		print(gpg_decrypt_file(filename = sys.argv[2], verbose = True))

	#-----------------------------------------------------------------------
	def test_gpg_encrypt_symmetric():
		print(encrypt_file_symmetric_gpg(filename = sys.argv[2], passphrase = sys.argv[3], verbose = True, comment = 'GNUmed testing'))

	#-----------------------------------------------------------------------
	def test_aes_encrypt():
		print(encrypt_file_symmetric_7z(filename = sys.argv[2], passphrase = sys.argv[3], comment = sys.argv[4], verbose = True))

	#-----------------------------------------------------------------------
	def test_encrypt_pdf():
		print(encrypt_pdf(filename = sys.argv[2], passphrase = sys.argv[3], verbose = True))
		#print(encrypt_pdf(filename = sys.argv[2], passphrase = 'PW mit Leerzeichen', verbose = True))

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
#			passphrase = 'PW mit Leerzeichen',
			verbose = True
		))

	#-----------------------------------------------------------------------
	def test_pdf_is_encrypted():
		print (
			sys.argv[2],
			is_encrypted_pdf(filename = sys.argv[2], verbose = True)
		)

	#-----------------------------------------------------------------------
	def test_decrypt_pdf():
		print (
			sys.argv[2],
			decrypt_pdf(filename = sys.argv[2], passphrase = sys.argv[3])
		)

	#-----------------------------------------------------------------------
	def test_encrypt_data_with_gpg():
		print(encrypt_data_with_gpg (
			data = sys.argv[2],
			recipient_key_files = [sys.argv[3], sys.argv[4]],
			comment = 'GNUmed testing',
			verbose = True
		))

	#-----------------------------------------------------------------------
	def test_encrypt_data_with_gpg_symmetrically():
		print(encrypt_data_with_gpg_symmetrically (
			data = sys.argv[2],
			comment = 'GNUmed testing',
			passphrase = '123456',
			verbose = True
		))

	#-----------------------------------------------------------------------
	def test_encrypt_data_with_7z():
		print(encrypt_data_with_7z (
			data = 'abcdefghijk',
			verbose = True,
			passphrase = '123456'
		))

	#-----------------------------------------------------------------------
	def test_encrypt_data():
		print(encrypt_data (
			data = 'abcdefghijk',
			recipient_key_files = [],
			verbose = True,
			symmetric_password = '123456',
			comment = 'GNUmed testing',
			retry_symmetric = True
		))

	#-----------------------------------------------------------------------
	# encryption
	#test_aes_encrypt()
	#test_encrypt_pdf()
	#test_gpg_encrypt_symmetric()
	#test_encrypt_file()

	# decryption
	#test_gpg_decrypt()

	#test_zip_archive_from_dir()
	#test_encrypted_zip_archive_from_dir()

	#test_pdf_is_encrypted()
	#test_decrypt_pdf()
	#test_encrypt_data_with_gpg()
	#test_encrypt_data_with_7z()
	#test_encrypt_data_with_gpg_symmetrically()
	test_encrypt_data()
