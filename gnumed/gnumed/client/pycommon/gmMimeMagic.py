# -*- coding: utf-8 -*-
"""magic.py
 determines a file type by its magic number

 (C)opyright 2000 Jason Petrone <jp@demonseed.net>
 All Rights Reserved

 Command Line Usage: running as `python3 magic.py file` will print
										 a description of what 'file' is.

 Module Usage:
		 magic.whatis(data): when passed a string 'data' containing 
												 binary or text data, a description of
												 what the data is will be returned.

		 magic.filedesc(filename): returns a description of what the file
													 'filename' contains.

Acknowledgements: This module has been pulled from the web. Thanks to
Jason Petrone for providing it to the community. It is based on his
__version__ = '0.1'
"""
# TODO
# - load alternative data on platforms (win: image/x-xbitmap)

#=================================================================
__author__ = "Jason Petrone <jp@demonseed.net>, Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

import re, struct, string
#=================================================================
magic = [
	[0, 'leshort', '=', 1538, 'application/x-alan-adventure-game'],
	[0, 'string', '=', 'TADS', 'application/x-tads-game'],
	[0, 'short', '=', 420, 'application/x-executable-file'],
	[0, 'short', '=', 421, 'application/x-executable-file'],
	[0, 'leshort', '=', 603, 'application/x-executable-file'],
	[0, 'string', '=', 'Core\001', 'application/x-executable-file'],
	[0, 'string', '=', 'AMANDA: TAPESTART DATE', 'application/x-amanda-header'],
	[0, 'belong', '=', 1011, 'application/x-executable-file'],
	[0, 'belong', '=', 999, 'application/x-library-file'],
	[0, 'belong', '=', 435, 'video/mpeg'],
	[0, 'belong', '=', 442, 'video/mpeg'],
	[0, 'beshort&0xfff0', '=', 65520, 'audio/mpeg'],
	[4, 'leshort', '=', 44817, 'video/fli'],
	[4, 'leshort', '=', 44818, 'video/flc'],
	[0, 'string', '=', 'MOVI', 'video/x-sgi-movie'],
	[4, 'string', '=', 'moov', 'video/quicktime'],
	[4, 'string', '=', 'mdat', 'video/quicktime'],
	[0, 'long', '=', 100554, 'application/x-apl-workspace'],
	[0, 'string', '=', 'FiLeStArTfIlEsTaRt', 'text/x-apple-binscii'],
	[0, 'string', '=', '\012GL', 'application/data'],
	[0, 'string', '=', 'v\377', 'application/data'],
	[0, 'string', '=', 'NuFile', 'application/data'],
	[0, 'string', '=', 'N\365F\351l\345', 'application/data'],
	[0, 'belong', '=', 333312, 'application/data'],
	[0, 'belong', '=', 333319, 'application/data'],
	[257, 'string', '=', 'ustar\000', 'application/x-tar'],
	[257, 'string', '=', 'ustar  \000', 'application/x-gtar'],
	[0, 'short', '=', 70707, 'application/x-cpio'],
	[0, 'short', '=', 143561, 'application/x-bcpio'],
	[0, 'string', '=', '070707', 'application/x-cpio'],
	[0, 'string', '=', '070701', 'application/x-cpio'],
	[0, 'string', '=', '070702', 'application/x-cpio'],
	[0, 'string', '=', '!<arch>\012debian', 'application/x-dpkg'],
	[0, 'long', '=', 177555, 'application/x-ar'],
	[0, 'short', '=', 177555, 'application/data'],
	[0, 'long', '=', 177545, 'application/data'],
	[0, 'short', '=', 177545, 'application/data'],
	[0, 'long', '=', 100554, 'application/x-apl-workspace'],
	[0, 'string', '=', '<ar>', 'application/x-ar'],
	[0, 'string', '=', '!<arch>\012__________E', 'application/x-ar'],
	[0, 'string', '=', '-h-', 'application/data'],
	[0, 'string', '=', '!<arch>', 'application/x-ar'],
	[0, 'string', '=', '<ar>', 'application/x-ar'],
	[0, 'string', '=', '<ar>', 'application/x-ar'],
	[0, 'belong', '=', 1711210496, 'application/x-ar'],
	[0, 'belong', '=', 1013019198, 'application/x-ar'],
	[0, 'long', '=', 557605234, 'application/x-ar'],
	[0, 'lelong', '=', 177555, 'application/data'],
	[0, 'leshort', '=', 177555, 'application/data'],
	[0, 'lelong', '=', 177545, 'application/data'],
	[0, 'leshort', '=', 177545, 'application/data'],
	[0, 'lelong', '=', 236525, 'application/data'],
	[0, 'lelong', '=', 236526, 'application/data'],
	[0, 'lelong&0x8080ffff', '=', 2074, 'application/x-arc'],
	[0, 'lelong&0x8080ffff', '=', 2330, 'application/x-arc'],
	[0, 'lelong&0x8080ffff', '=', 538, 'application/x-arc'],
	[0, 'lelong&0x8080ffff', '=', 794, 'application/x-arc'],
	[0, 'lelong&0x8080ffff', '=', 1050, 'application/x-arc'],
	[0, 'lelong&0x8080ffff', '=', 1562, 'application/x-arc'],
	[0, 'string', '=', '\032archive', 'application/data'],
	[0, 'leshort', '=', 60000, 'application/x-arj'],
	[0, 'string', '=', 'HPAK', 'application/data'],
	[0, 'string', '=', '\351,\001JAM application/data', ''],
	[2, 'string', '=', '-lh0-', 'application/x-lha'],
	[2, 'string', '=', '-lh1-', 'application/x-lha'],
	[2, 'string', '=', '-lz4-', 'application/x-lha'],
	[2, 'string', '=', '-lz5-', 'application/x-lha'],
	[2, 'string', '=', '-lzs-', 'application/x-lha'],
	[2, 'string', '=', '-lh -', 'application/x-lha'],
	[2, 'string', '=', '-lhd-', 'application/x-lha'],
	[2, 'string', '=', '-lh2-', 'application/x-lha'],
	[2, 'string', '=', '-lh3-', 'application/x-lha'],
	[2, 'string', '=', '-lh4-', 'application/x-lha'],
	[2, 'string', '=', '-lh5-', 'application/x-lha'],
	[0, 'string', '=', 'Rar!', 'application/x-rar'],
	[0, 'string', '=', 'SQSH', 'application/data'],
	[0, 'string', '=', 'UC2\032', 'application/data'],
	[0, 'string', '=', 'PK\003\004', 'application/zip'],
	[20, 'lelong', '=', 4257523676, 'application/x-zoo'],
	[10, 'string', '=', '# This is a shell archive', 'application/x-shar'],
	[0, 'string', '=', '*STA', 'application/data'],
	[0, 'string', '=', '2278', 'application/data'],
	[0, 'beshort', '=', 560, 'application/x-executable-file'],
	[0, 'beshort', '=', 561, 'application/x-executable-file'],
	[0, 'string', '=', '\000\004\036\212\200', 'application/core'],
	[0, 'string', '=', '.snd', 'audio/basic'],
	[0, 'lelong', '=', 6583086, 'audio/basic'],
	[0, 'string', '=', 'MThd', 'audio/midi'],
	[0, 'string', '=', 'CTMF', 'audio/x-cmf'],
	[0, 'string', '=', 'SBI', 'audio/x-sbi'],
	[0, 'string', '=', 'Creative Voice File', 'audio/x-voc'],
	[0, 'belong', '=', 1314148939, 'audio/x-multitrack'],
	[0, 'string', '=', 'RIFF', 'audio/x-wav'],
	[0, 'string', '=', 'EMOD', 'audio/x-emod'],
	[0, 'belong', '=', 779248125, 'audio/x-pn-realaudio'],
	[0, 'string', '=', 'MTM', 'audio/x-multitrack'],
	[0, 'string', '=', 'if', 'audio/x-669-mod'],
	[0, 'string', '=', 'FAR', 'audio/mod'],
	[0, 'string', '=', 'MAS_U', 'audio/x-multimate-mod'],
	[44, 'string', '=', 'SCRM', 'audio/x-st3-mod'],
	[0, 'string', '=', 'GF1PATCH110\000ID#000002\000', 'audio/x-gus-patch'],
	[0, 'string', '=', 'GF1PATCH100\000ID#000002\000', 'audio/x-gus-patch'],
	[0, 'string', '=', 'JN', 'audio/x-669-mod'],
	[0, 'string', '=', 'UN05', 'audio/x-mikmod-uni'],
	[0, 'string', '=', 'Extended Module:', 'audio/x-ft2-mod'],
	[21, 'string', '=', '!SCREAM!', 'audio/x-st2-mod'],
	[1080, 'string', '=', 'M.K.', 'audio/x-protracker-mod'],
	[1080, 'string', '=', 'M!K!', 'audio/x-protracker-mod'],
	[1080, 'string', '=', 'FLT4', 'audio/x-startracker-mod'],
	[1080, 'string', '=', '4CHN', 'audio/x-fasttracker-mod'],
	[1080, 'string', '=', '6CHN', 'audio/x-fasttracker-mod'],
	[1080, 'string', '=', '8CHN', 'audio/x-fasttracker-mod'],
	[1080, 'string', '=', 'CD81', 'audio/x-oktalyzer-mod'],
	[1080, 'string', '=', 'OKTA', 'audio/x-oktalyzer-mod'],
	[1080, 'string', '=', '16CN', 'audio/x-taketracker-mod'],
	[1080, 'string', '=', '32CN', 'audio/x-taketracker-mod'],
	[0, 'string', '=', 'TOC', 'audio/x-toc'],
	[0, 'short', '=', 3401, 'application/x-executable-file'],
	[0, 'long', '=', 406, 'application/x-executable-file'],
	[0, 'short', '=', 406, 'application/x-executable-file'],
	[0, 'short', '=', 3001, 'application/x-executable-file'],
	[0, 'lelong', '=', 314, 'application/x-executable-file'],
	[0, 'string', '=', '//', 'text/cpp'],
	[0, 'string', '=', '\\\\1cw\\', 'application/data'],
	[0, 'string', '=', '\\\\1cw', 'application/data'],
	[0, 'belong&0xffffff00', '=', 2231440384, 'application/data'],
	[0, 'belong&0xffffff00', '=', 2231487232, 'application/data'],
	[0, 'short', '=', 575, 'application/x-executable-file'],
	[0, 'short', '=', 577, 'application/x-executable-file'],
	[4, 'string', '=', 'pipe', 'application/data'],
	[4, 'string', '=', 'prof', 'application/data'],
	[0, 'string', '=', ': shell', 'application/data'],
	[0, 'string', '=', '#!/bin/sh', 'application/x-sh'],
	[0, 'string', '=', '#! /bin/sh', 'application/x-sh'],
	[0, 'string', '=', '#! /bin/sh', 'application/x-sh'],
	[0, 'string', '=', '#!/bin/csh', 'application/x-csh'],
	[0, 'string', '=', '#! /bin/csh', 'application/x-csh'],
	[0, 'string', '=', '#! /bin/csh', 'application/x-csh'],
	[0, 'string', '=', '#!/bin/ksh', 'application/x-ksh'],
	[0, 'string', '=', '#! /bin/ksh', 'application/x-ksh'],
	[0, 'string', '=', '#! /bin/ksh', 'application/x-ksh'],
	[0, 'string', '=', '#!/bin/tcsh', 'application/x-csh'],
	[0, 'string', '=', '#! /bin/tcsh', 'application/x-csh'],
	[0, 'string', '=', '#! /bin/tcsh', 'application/x-csh'],
	[0, 'string', '=', '#!/usr/local/tcsh', 'application/x-csh'],
	[0, 'string', '=', '#! /usr/local/tcsh', 'application/x-csh'],
	[0, 'string', '=', '#!/usr/local/bin/tcsh', 'application/x-csh'],
	[0, 'string', '=', '#! /usr/local/bin/tcsh', 'application/x-csh'],
	[0, 'string', '=', '#! /usr/local/bin/tcsh', 'application/x-csh'],
	[0, 'string', '=', '#!/usr/local/bin/zsh', 'application/x-zsh'],
	[0, 'string', '=', '#! /usr/local/bin/zsh', 'application/x-zsh'],
	[0, 'string', '=', '#! /usr/local/bin/zsh', 'application/x-zsh'],
	[0, 'string', '=', '#!/usr/local/bin/ash', 'application/x-sh'],
	[0, 'string', '=', '#! /usr/local/bin/ash', 'application/x-zsh'],
	[0, 'string', '=', '#! /usr/local/bin/ash', 'application/x-zsh'],
	[0, 'string', '=', '#!/usr/local/bin/ae', 'text/script'],
	[0, 'string', '=', '#! /usr/local/bin/ae', 'text/script'],
	[0, 'string', '=', '#! /usr/local/bin/ae', 'text/script'],
	[0, 'string', '=', '#!/bin/nawk', 'application/x-awk'],
	[0, 'string', '=', '#! /bin/nawk', 'application/x-awk'],
	[0, 'string', '=', '#! /bin/nawk', 'application/x-awk'],
	[0, 'string', '=', '#!/usr/bin/nawk', 'application/x-awk'],
	[0, 'string', '=', '#! /usr/bin/nawk', 'application/x-awk'],
	[0, 'string', '=', '#! /usr/bin/nawk', 'application/x-awk'],
	[0, 'string', '=', '#!/usr/local/bin/nawk', 'application/x-awk'],
	[0, 'string', '=', '#! /usr/local/bin/nawk', 'application/x-awk'],
	[0, 'string', '=', '#! /usr/local/bin/nawk', 'application/x-awk'],
	[0, 'string', '=', '#!/bin/gawk', 'application/x-awk'],
	[0, 'string', '=', '#! /bin/gawk', 'application/x-awk'],
	[0, 'string', '=', '#! /bin/gawk', 'application/x-awk'],
	[0, 'string', '=', '#!/usr/bin/gawk', 'application/x-awk'],
	[0, 'string', '=', '#! /usr/bin/gawk', 'application/x-awk'],
	[0, 'string', '=', '#! /usr/bin/gawk', 'application/x-awk'],
	[0, 'string', '=', '#!/usr/local/bin/gawk', 'application/x-awk'],
	[0, 'string', '=', '#! /usr/local/bin/gawk', 'application/x-awk'],
	[0, 'string', '=', '#! /usr/local/bin/gawk', 'application/x-awk'],
	[0, 'string', '=', '#!/bin/awk', 'application/x-awk'],
	[0, 'string', '=', '#! /bin/awk', 'application/x-awk'],
	[0, 'string', '=', '#! /bin/awk', 'application/x-awk'],
	[0, 'string', '=', '#!/usr/bin/awk', 'application/x-awk'],
	[0, 'string', '=', '#! /usr/bin/awk', 'application/x-awk'],
	[0, 'string', '=', '#! /usr/bin/awk', 'application/x-awk'],
	[0, 'string', '=', 'BEGIN', 'application/x-awk'],
	[0, 'string', '=', '#!/bin/perl', 'application/x-perl'],
	[0, 'string', '=', '#! /bin/perl', 'application/x-perl'],
	[0, 'string', '=', '#! /bin/perl', 'application/x-perl'],
	[0, 'string', '=', 'eval "exec /bin/perl', 'application/x-perl'],
	[0, 'string', '=', '#!/usr/bin/perl', 'application/x-perl'],
	[0, 'string', '=', '#! /usr/bin/perl', 'application/x-perl'],
	[0, 'string', '=', '#! /usr/bin/perl', 'application/x-perl'],
	[0, 'string', '=', 'eval "exec /usr/bin/perl', 'application/x-perl'],
	[0, 'string', '=', '#!/usr/local/bin/perl', 'application/x-perl'],
	[0, 'string', '=', '#! /usr/local/bin/perl', 'application/x-perl'],
	[0, 'string', '=', '#! /usr/local/bin/perl', 'application/x-perl'],
	[0, 'string', '=', 'eval "exec /usr/local/bin/perl', 'application/x-perl'],
	[0, 'string', '=', '#!/bin/python3', 'application/x-python'],
	[0, 'string', '=', '#! /bin/python3', 'application/x-python'],
	[0, 'string', '=', '#! /bin/python3', 'application/x-python'],
	[0, 'string', '=', 'eval "exec /bin/python3', 'application/x-python'],
	[0, 'string', '=', '#!/usr/bin/python3', 'application/x-python'],
	[0, 'string', '=', '#! /usr/bin/python3', 'application/x-python'],
	[0, 'string', '=', '#! /usr/bin/python3', 'application/x-python'],
	[0, 'string', '=', 'eval "exec /usr/bin/python3', 'application/x-python'],
	[0, 'string', '=', '#!/usr/local/bin/python3', 'application/x-python'],
	[0, 'string', '=', '#! /usr/local/bin/python3', 'application/x-python'],
	[0, 'string', '=', '#! /usr/local/bin/python3', 'application/x-python'],
	[0, 'string', '=', 'eval "exec /usr/local/bin/python3', 'application/x-python'],
	[0, 'string', '=', '#!/usr/bin/env python3', 'application/x-python'],
	[0, 'string', '=', '#! /usr/bin/env python3', 'application/x-python'],
	[0, 'string', '=', '#!/bin/rc', 'text/script'],
	[0, 'string', '=', '#! /bin/rc', 'text/script'],
	[0, 'string', '=', '#! /bin/rc', 'text/script'],
	[0, 'string', '=', '#!/bin/bash', 'application/x-sh'],
	[0, 'string', '=', '#! /bin/bash', 'application/x-sh'],
	[0, 'string', '=', '#! /bin/bash', 'application/x-sh'],
	[0, 'string', '=', '#!/usr/local/bin/bash', 'application/x-sh'],
	[0, 'string', '=', '#! /usr/local/bin/bash', 'application/x-sh'],
	[0, 'string', '=', '#! /usr/local/bin/bash', 'application/x-sh'],
	[0, 'string', '=', '#! /', 'text/script'],
	[0, 'string', '=', '#! /', 'text/script'],
	[0, 'string', '=', '#!/', 'text/script'],
	[0, 'string', '=', '#! text/script', ''],
	[0, 'string', '=', '\037\235', 'application/compress'],
	[0, 'string', '=', '\037\213', 'application/x-gzip'],
	[0, 'string', '=', '\037\036', 'application/data'],
	[0, 'short', '=', 17437, 'application/data'],
	[0, 'short', '=', 8191, 'application/data'],
	[0, 'string', '=', '\377\037', 'application/data'],
	[0, 'short', '=', 145405, 'application/data'],
	[0, 'string', '=', 'BZh', 'application/x-bzip2'],
	[0, 'leshort', '=', 65398, 'application/data'],
	[0, 'leshort', '=', 65142, 'application/data'],
	[0, 'leshort', '=', 64886, 'application/x-lzh'],
	[0, 'string', '=', '\037\237', 'application/data'],
	[0, 'string', '=', '\037\236', 'application/data'],
	[0, 'string', '=', '\037\240', 'application/data'],
	[0, 'string', '=', 'BZ', 'application/x-bzip'],
	[0, 'string', '=', '\211LZO\000\015\012\032\012', 'application/data'],
	[0, 'belong', '=', 507, 'application/x-object-file'],
	[0, 'belong', '=', 513, 'application/x-executable-file'],
	[0, 'belong', '=', 515, 'application/x-executable-file'],
	[0, 'belong', '=', 517, 'application/x-executable-file'],
	[0, 'belong', '=', 70231, 'application/core'],
	[24, 'belong', '=', 60011, 'application/data'],
	[24, 'belong', '=', 60012, 'application/data'],
	[24, 'belong', '=', 60013, 'application/data'],
	[24, 'belong', '=', 60014, 'application/data'],
	[0, 'belong', '=', 601, 'application/x-object-file'],
	[0, 'belong', '=', 607, 'application/data'],
	[0, 'belong', '=', 324508366, 'application/x-gdbm'],
	[0, 'lelong', '=', 324508366, 'application/x-gdbm'],
	[0, 'string', '=', 'GDBM', 'application/x-gdbm'],
	[0, 'belong', '=', 398689, 'application/x-db'],
	[0, 'belong', '=', 340322, 'application/x-db'],
	[0, 'string', '=', '<list>\012<protocol bbn-m', 'application/data'],
	[0, 'string', '=', 'diff text/x-patch', ''],
	[0, 'string', '=', '*** text/x-patch', ''],
	[0, 'string', '=', 'Only in text/x-patch', ''],
	[0, 'string', '=', 'Common subdirectories: text/x-patch', ''],
	[0, 'string', '=', '!<arch>\012________64E', 'application/data'],
	[0, 'leshort', '=', 387, 'application/x-executable-file'],
	[0, 'leshort', '=', 392, 'application/x-executable-file'],
	[0, 'leshort', '=', 399, 'application/x-object-file'],
	[0, 'string', '=', '\377\377\177', 'application/data'],
	[0, 'string', '=', '\377\377|', 'application/data'],
	[0, 'string', '=', '\377\377~', 'application/data'],
	[0, 'string', '=', '\033c\033', 'application/data'],
	[0, 'long', '=', 4553207, 'image/x11'],
	[0, 'string', '=', '!<PDF>!\012', 'application/x-prof'],
	[0, 'short', '=', 1281, 'application/x-locale'],
	[24, 'belong', '=', 60012, 'application/x-dump'],
	[24, 'belong', '=', 60011, 'application/x-dump'],
	[24, 'lelong', '=', 60012, 'application/x-dump'],
	[24, 'lelong', '=', 60011, 'application/x-dump'],
	[0, 'string', '=', '\177ELF', 'application/x-executable-file'],
	[0, 'short', '=', 340, 'application/data'],
	[0, 'short', '=', 341, 'application/x-executable-file'],
	[1080, 'leshort', '=', 61267, 'application/x-linux-ext2fs'],
	[0, 'string', '=', '\366\366\366\366', 'application/x-pc-floppy'],
	[774, 'beshort', '=', 55998, 'application/data'],
	[510, 'leshort', '=', 43605, 'application/data'],
	[1040, 'leshort', '=', 4991, 'application/x-filesystem'],
	[1040, 'leshort', '=', 5007, 'application/x-filesystem'],
	[1040, 'leshort', '=', 9320, 'application/x-filesystem'],
	[1040, 'leshort', '=', 9336, 'application/x-filesystem'],
	[0, 'string', '=', '-rom1fs-\000', 'application/x-filesystem'],
	[395, 'string', '=', 'OS/2', 'application/x-bootable'],
	[0, 'string', '=', 'FONT', 'font/x-vfont'],
	[0, 'short', '=', 436, 'font/x-vfont'],
	[0, 'short', '=', 17001, 'font/x-vfont'],
	[0, 'string', '=', '%!PS-AdobeFont-1.0', 'font/type1'],
	[6, 'string', '=', '%!PS-AdobeFont-1.0', 'font/type1'],
	[0, 'belong', '=', 4, 'font/x-snf'],
	[0, 'lelong', '=', 4, 'font/x-snf'],
	[0, 'string', '=', 'STARTFONT font/x-bdf', ''],
	[0, 'string', '=', '\001fcp', 'font/x-pcf'],
	[0, 'string', '=', 'D1.0\015', 'font/x-speedo'],
	[0, 'string', '=', 'flf', 'font/x-figlet'],
	[0, 'string', '=', 'flc', 'application/x-font'],
	[0, 'belong', '=', 335698201, 'font/x-libgrx'],
	[0, 'belong', '=', 4282797902, 'font/x-dos'],
	[7, 'belong', '=', 4540225, 'font/x-dos'],
	[7, 'belong', '=', 5654852, 'font/x-dos'],
	[4098, 'string', '=', 'DOSFONT', 'font/x-dos'],
	[0, 'string', '=', '<MakerFile', 'application/x-framemaker'],
	[0, 'string', '=', '<MIFFile', 'application/x-framemaker'],
	[0, 'string', '=', '<MakerDictionary', 'application/x-framemaker'],
	[0, 'string', '=', '<MakerScreenFont', 'font/x-framemaker'],
	[0, 'string', '=', '<MML', 'application/x-framemaker'],
	[0, 'string', '=', '<BookFile', 'application/x-framemaker'],
	[0, 'string', '=', '<Maker', 'application/x-framemaker'],
	[0, 'lelong&0377777777', '=', 41400407, 'application/x-executable-file'],
	[0, 'lelong&0377777777', '=', 41400410, 'application/x-executable-file'],
	[0, 'lelong&0377777777', '=', 41400413, 'application/x-executable-file'],
	[0, 'lelong&0377777777', '=', 41400314, 'application/x-executable-file'],
	[7, 'string', '=', '\357\020\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000', 'application/core'],
	[0, 'lelong', '=', 11421044151, 'application/data'],
	[0, 'string', '=', 'GIMP Gradient', 'application/x-gimp-gradient'],
	[0, 'string', '=', 'gimp xcf', 'application/x-gimp-image'],
	[20, 'string', '=', 'GPAT', 'application/x-gimp-pattern'],
	[20, 'string', '=', 'GIMP', 'application/x-gimp-brush'],
	[0, 'string', '=', '\336\022\004\225', 'application/x-locale'],
	[0, 'string', '=', '\225\004\022\336', 'application/x-locale'],
	[0, 'beshort', '=', 627, 'application/x-executable-file'],
	[0, 'beshort', '=', 624, 'application/x-executable-file'],
	[0, 'string', '=', '\000\001\000\000\000', 'font/ttf'],
	[0, 'long', '=', 1203604016, 'application/data'],
	[0, 'long', '=', 1702407010, 'application/data'],
	[0, 'long', '=', 1003405017, 'application/data'],
	[0, 'long', '=', 1602007412, 'application/data'],
	[0, 'belong', '=', 34603270, 'application/x-object-file'],
	[0, 'belong', '=', 34603271, 'application/x-executable-file'],
	[0, 'belong', '=', 34603272, 'application/x-executable-file'],
	[0, 'belong', '=', 34603275, 'application/x-executable-file'],
	[0, 'belong', '=', 34603278, 'application/x-library-file'],
	[0, 'belong', '=', 34603277, 'application/x-library-file'],
	[0, 'belong', '=', 34865414, 'application/x-object-file'],
	[0, 'belong', '=', 34865415, 'application/x-executable-file'],
	[0, 'belong', '=', 34865416, 'application/x-executable-file'],
	[0, 'belong', '=', 34865419, 'application/x-executable-file'],
	[0, 'belong', '=', 34865422, 'application/x-library-file'],
	[0, 'belong', '=', 34865421, 'application/x-object-file'],
	[0, 'belong', '=', 34275590, 'application/x-object-file'],
	[0, 'belong', '=', 34275591, 'application/x-executable-file'],
	[0, 'belong', '=', 34275592, 'application/x-executable-file'],
	[0, 'belong', '=', 34275595, 'application/x-executable-file'],
	[0, 'belong', '=', 34275598, 'application/x-library-file'],
	[0, 'belong', '=', 34275597, 'application/x-library-file'],
	[0, 'belong', '=', 557605234, 'application/x-ar'],
	[0, 'long', '=', 34078982, 'application/x-executable-file'],
	[0, 'long', '=', 34078983, 'application/x-executable-file'],
	[0, 'long', '=', 34078984, 'application/x-executable-file'],
	[0, 'belong', '=', 34341128, 'application/x-executable-file'],
	[0, 'belong', '=', 34341127, 'application/x-executable-file'],
	[0, 'belong', '=', 34341131, 'application/x-executable-file'],
	[0, 'belong', '=', 34341126, 'application/x-executable-file'],
	[0, 'belong', '=', 34210056, 'application/x-executable-file'],
	[0, 'belong', '=', 34210055, 'application/x-executable-file'],
	[0, 'belong', '=', 34341134, 'application/x-library-file'],
	[0, 'belong', '=', 34341133, 'application/x-library-file'],
	[0, 'long', '=', 65381, 'application/x-library-file'],
	[0, 'long', '=', 34275173, 'application/x-library-file'],
	[0, 'long', '=', 34406245, 'application/x-library-file'],
	[0, 'long', '=', 34144101, 'application/x-library-file'],
	[0, 'long', '=', 22552998, 'application/core'],
	[0, 'long', '=', 1302851304, 'font/x-hp-windows'],
	[0, 'string', '=', 'Bitmapfile', 'image/unknown'],
	[0, 'string', '=', 'IMGfile', 'CIS image/unknown'],
	[0, 'long', '=', 34341132, 'application/x-lisp'],
	[0, 'string', '=', 'msgcat01', 'application/x-locale'],
	[0, 'string', '=', 'HPHP48-', 'HP48 binary'],
	[0, 'string', '=', '%%HP:', 'HP48 text'],
	[0, 'beshort', '=', 200, 'hp200 (68010) BSD'],
	[0, 'beshort', '=', 300, 'hp300 (68020+68881) BSD'],
	[0, 'beshort', '=', 537, '370 XA sysV executable'],
	[0, 'beshort', '=', 532, '370 XA sysV pure executable'],
	[0, 'beshort', '=', 54001, '370 sysV pure executable'],
	[0, 'beshort', '=', 55001, '370 XA sysV pure executable'],
	[0, 'beshort', '=', 56401, '370 sysV executable'],
	[0, 'beshort', '=', 57401, '370 XA sysV executable'],
	[0, 'beshort', '=', 531, 'SVR2 executable (Amdahl-UTS)'],
	[0, 'beshort', '=', 534, 'SVR2 pure executable (Amdahl-UTS)'],
	[0, 'beshort', '=', 530, 'SVR2 pure executable (USS/370)'],
	[0, 'beshort', '=', 535, 'SVR2 executable (USS/370)'],
	[0, 'beshort', '=', 479, 'executable (RISC System/6000 V3.1) or obj module'],
	[0, 'beshort', '=', 260, 'shared library'],
	[0, 'beshort', '=', 261, 'ctab data'],
	[0, 'beshort', '=', 65028, 'structured file'],
	[0, 'string', '=', '0xabcdef', 'AIX message catalog'],
	[0, 'belong', '=', 505, 'AIX compiled message catalog'],
	[0, 'string', '=', '<aiaff>', 'archive'],
	[0, 'string', '=', 'FORM', 'IFF data'],
	[0, 'string', '=', 'P1', 'image/x-portable-bitmap'],
	[0, 'string', '=', 'P2', 'image/x-portable-graymap'],
	[0, 'string', '=', 'P3', 'image/x-portable-pixmap'],
	[0, 'string', '=', 'P4', 'image/x-portable-bitmap'],
	[0, 'string', '=', 'P5', 'image/x-portable-graymap'],
	[0, 'string', '=', 'P6', 'image/x-portable-pixmap'],
	[0, 'string', '=', 'IIN1', 'image/tiff'],
	[0, 'string', '=', 'MM\000*', 'image/tiff'],
	[0, 'string', '=', 'II*\000', 'image/tiff'],
	[0, 'string', '=', '\211PNG', 'image/x-png'],
	[1, 'string', '=', 'PNG', 'image/x-png'],
	[0, 'string', '=', 'GIF8', 'image/gif'],
	[0, 'string', '=', '\361\000@\273', 'image/x-cmu-raster'],
	[0, 'string', '=', 'id=ImageMagick', 'MIFF image data'],
	[0, 'long', '=', 1123028772, 'Artisan image data'],
	[0, 'string', '=', '#FIG', 'FIG image text'],
	[0, 'string', '=', 'ARF_BEGARF', 'PHIGS clear text archive'],
	[0, 'string', '=', '@(#)SunPHIGS', 'SunPHIGS'],
	[0, 'string', '=', 'GKSM', 'GKS Metafile'],
	[0, 'string', '=', 'BEGMF', 'clear text Computer Graphics Metafile'],
	[0, 'beshort&0xffe0', '=', 32, 'binary Computer Graphics Metafile'],
	[0, 'beshort', '=', 12320, 'character Computer Graphics Metafile'],
	[0, 'string', '=', 'yz', 'MGR bitmap, modern format, 8-bit aligned'],
	[0, 'string', '=', 'zz', 'MGR bitmap, old format, 1-bit deep, 16-bit aligned'],
	[0, 'string', '=', 'xz', 'MGR bitmap, old format, 1-bit deep, 32-bit aligned'],
	[0, 'string', '=', 'yx', 'MGR bitmap, modern format, squeezed'],
	[0, 'string', '=', '%bitmap\000', 'FBM image data'],
	[1, 'string', '=', 'PC Research, Inc', 'group 3 fax data'],
	[0, 'beshort', '=', 65496, 'image/jpeg'],
	[0, 'string', '=', 'hsi1', 'image/x-jpeg-proprietary'],
	[0, 'string', '=', 'BM', 'image/x-ms-bmp'],
	[0, 'string', '=', 'IC', 'image/x-ico'],
	[0, 'string', '=', 'PI', 'PC pointer image data'],
	[0, 'string', '=', 'CI', 'PC color icon data'],
	[0, 'string', '=', 'CP', 'PC color pointer image data'],
	[0, 'string', '=', '/* XPM */', 'X pixmap image text'],
	[0, 'leshort', '=', 52306, 'RLE image data,'],
	[0, 'string', '=', 'Imagefile version-', 'iff image data'],
	[0, 'belong', '=', 1504078485, 'x/x-image-sun-raster'],
	[0, 'beshort', '=', 474, 'x/x-image-sgi'],
	[0, 'string', '=', 'IT01', 'FIT image data'],
	[0, 'string', '=', 'IT02', 'FIT image data'],
	[2048, 'string', '=', 'PCD_IPI', 'x/x-photo-cd-pack-file'],
	[0, 'string', '=', 'PCD_OPA', 'x/x-photo-cd-overfiew-file'],
	[0, 'string', '=', 'SIMPLE  =', 'FITS image data'],
	[0, 'string', '=', 'This is a BitMap file', 'Lisp Machine bit-array-file'],
	[0, 'string', '=', '!!', 'Bennet Yee\'s "face" format'],
	[0, 'beshort', '=', 4112, 'PEX Binary Archive'],
	[3000, 'string', '=', 'Visio (TM) Drawing', '%s'],
	[0, 'leshort', '=', 502, 'basic-16 executable'],
	[0, 'leshort', '=', 503, 'basic-16 executable (TV)'],
	[0, 'leshort', '=', 510, 'application/x-executable-file'],
	[0, 'leshort', '=', 511, 'application/x-executable-file'],
	[0, 'leshort', '=', 512, 'application/x-executable-file'],
	[0, 'leshort', '=', 522, 'application/x-executable-file'],
	[0, 'leshort', '=', 514, 'application/x-executable-file'],
	[0, 'string', '=', '\210OPS', 'Interleaf saved data'],
	[0, 'string', '=', '<!OPS', 'Interleaf document text'],
	[4, 'string', '=', 'pgscriptver', 'IslandWrite document'],
	[13, 'string', '=', 'DrawFile', 'IslandDraw document'],
	[0, 'leshort&0xFFFC', '=', 38400, 'little endian ispell'],
	[0, 'beshort&0xFFFC', '=', 38400, 'big endian ispell'],
	[0, 'belong', '=', 3405691582, 'compiled Java class data,'],
	[0, 'beshort', '=', 44269, 'Java serialization data'],
	[0, 'string', '=', 'KarmaRHD', 'Version Karma Data Structure Version'],
	[0, 'string', '=', 'lect', 'DEC SRC Virtual Paper Lectern file'],
	[53, 'string', '=', 'yyprevious', 'C program text (from lex)'],
	[21, 'string', '=', 'generated by flex', 'C program text (from flex)'],
	[0, 'string', '=', '%{', 'lex description text'],
	[0, 'short', '=', 32768, 'lif file'],
	[0, 'lelong', '=', 6553863, 'Linux/i386 impure executable (OMAGIC)'],
	[0, 'lelong', '=', 6553864, 'Linux/i386 pure executable (NMAGIC)'],
	[0, 'lelong', '=', 6553867, 'Linux/i386 demand-paged executable (ZMAGIC)'],
	[0, 'lelong', '=', 6553804, 'Linux/i386 demand-paged executable (QMAGIC)'],
	[0, 'string', '=', '\007\001\000', 'Linux/i386 object file'],
	[0, 'string', '=', '\001\003\020\004', 'Linux-8086 impure executable'],
	[0, 'string', '=', '\001\003 \004', 'Linux-8086 executable'],
	[0, 'string', '=', '\243\206\001\000', 'Linux-8086 object file'],
	[0, 'string', '=', '\001\003\020\020', 'Minix-386 impure executable'],
	[0, 'string', '=', '\001\003 \020', 'Minix-386 executable'],
	[0, 'string', '=', '*nazgul*', 'Linux compiled message catalog'],
	[216, 'lelong', '=', 421, 'Linux/i386 core file'],
	[2, 'string', '=', 'LILO', 'Linux/i386 LILO boot/chain loader'],
	[0, 'string', '=', '0.9', ''],
	[0, 'leshort', '=', 1078, 'font/linux-psf'],
	[4086, 'string', '=', 'SWAP-SPACE', 'Linux/i386 swap file'],
	[0, 'leshort', '=', 387, 'ECOFF alpha'],
	[514, 'string', '=', 'HdrS', 'Linux kernel'],
	[0, 'belong', '=', 3099592590, 'Linux kernel'],
	[0, 'string', '=', 'Begin3', 'Linux Software Map entry text'],
	[0, 'string', '=', ';;', 'Lisp/Scheme program text'],
	[0, 'string', '=', '\012(', 'byte-compiled Emacs-Lisp program data'],
	[0, 'string', '=', ';ELC\023\000\000\000', 'byte-compiled Emacs-Lisp program data'],
	[0, 'string', '=', "(SYSTEM::VERSION '", 'CLISP byte-compiled Lisp program text'],
	[0, 'long', '=', 1886817234, 'CLISP memory image data'],
	[0, 'long', '=', 3532355184, 'CLISP memory image data, other endian'],
	[0, 'long', '=', 3725722773, 'GNU-format message catalog data'],
	[0, 'long', '=', 2500072158, 'GNU-format message catalog data'],
	[0, 'belong', '=', 3405691582, 'mach-o fat file'],
	[0, 'belong', '=', 4277009102, 'mach-o'],
	[11, 'string', '=', 'must be converted with BinHex', 'BinHex binary text'],
	[0, 'string', '=', 'SIT!', 'StuffIt Archive (data)'],
	[65, 'string', '=', 'SIT!', 'StuffIt Archive (rsrc + data)'],
	[0, 'string', '=', 'SITD', 'StuffIt Deluxe (data)'],
	[65, 'string', '=', 'SITD', 'StuffIt Deluxe (rsrc + data)'],
	[0, 'string', '=', 'Seg', 'StuffIt Deluxe Segment (data)'],
	[65, 'string', '=', 'Seg', 'StuffIt Deluxe Segment (rsrc + data)'],
	[0, 'string', '=', 'APPL', 'Macintosh Application (data)'],
	[65, 'string', '=', 'APPL', 'Macintosh Application (rsrc + data)'],
	[0, 'string', '=', 'zsys', 'Macintosh System File (data)'],
	[65, 'string', '=', 'zsys', 'Macintosh System File(rsrc + data)'],
	[0, 'string', '=', 'FNDR', 'Macintosh Finder (data)'],
	[65, 'string', '=', 'FNDR', 'Macintosh Finder(rsrc + data)'],
	[0, 'string', '=', 'libr', 'Macintosh Library (data)'],
	[65, 'string', '=', 'libr', 'Macintosh Library(rsrc + data)'],
	[0, 'string', '=', 'shlb', 'Macintosh Shared Library (data)'],
	[65, 'string', '=', 'shlb', 'Macintosh Shared Library(rsrc + data)'],
	[0, 'string', '=', 'cdev', 'Macintosh Control Panel (data)'],
	[65, 'string', '=', 'cdev', 'Macintosh Control Panel(rsrc + data)'],
	[0, 'string', '=', 'INIT', 'Macintosh Extension (data)'],
	[65, 'string', '=', 'INIT', 'Macintosh Extension(rsrc + data)'],
	[0, 'string', '=', 'FFIL', 'font/ttf'],
	[65, 'string', '=', 'FFIL', 'font/ttf'],
	[0, 'string', '=', 'LWFN', 'font/type1'],
	[65, 'string', '=', 'LWFN', 'font/type1'],
	[0, 'string', '=', 'PACT', 'Macintosh Compact Pro Archive (data)'],
	[65, 'string', '=', 'PACT', 'Macintosh Compact Pro Archive(rsrc + data)'],
	[0, 'string', '=', 'ttro', 'Macintosh TeachText File (data)'],
	[65, 'string', '=', 'ttro', 'Macintosh TeachText File(rsrc + data)'],
	[0, 'string', '=', 'TEXT', 'Macintosh TeachText File (data)'],
	[65, 'string', '=', 'TEXT', 'Macintosh TeachText File(rsrc + data)'],
	[0, 'string', '=', 'PDF', 'Macintosh PDF File (data)'],
	[65, 'string', '=', 'PDF', 'Macintosh PDF File(rsrc + data)'],
	[0, 'string', '=', '# Magic', 'magic text file for file(1) cmd'],
	[0, 'string', '=', 'Relay-Version:', 'old news text'],
	[0, 'string', '=', '#! rnews', 'batched news text'],
	[0, 'string', '=', 'N#! rnews', 'mailed, batched news text'],
	[0, 'string', '=', 'Forward to', 'mail forwarding text'],
	[0, 'string', '=', 'Pipe to', 'mail piping text'],
	[0, 'string', '=', 'Return-Path:', 'message/rfc822'],
	[0, 'string', '=', 'Path:', 'message/news'],
	[0, 'string', '=', 'Xref:', 'message/news'],
	[0, 'string', '=', 'From:', 'message/rfc822'],
	[0, 'string', '=', 'Article', 'message/news'],
	[0, 'string', '=', 'BABYL', 'message/x-gnu-rmail'],
	[0, 'string', '=', 'Received:', 'message/rfc822'],
	[0, 'string', '=', 'MIME-Version:', 'MIME entity text'],
	[0, 'string', '=', 'Content-Type: ', ''],
	[0, 'string', '=', 'Content-Type:', ''],
	[0, 'long', '=', 31415, 'Mirage Assembler m.out executable'],
	[0, 'string', '=', '\311\304', 'ID tags data'],
	[0, 'string', '=', '\001\001\001\001', 'MMDF mailbox'],
	[4, 'string', '=', 'Research,', 'Digifax-G3-File'],
	[0, 'short', '=', 256, 'raw G3 data, byte-padded'],
	[0, 'short', '=', 5120, 'raw G3 data'],
	[0, 'string', '=', 'RMD1', 'raw modem data'],
	[0, 'string', '=', 'PVF1\012', 'portable voice format'],
	[0, 'string', '=', 'PVF2\012', 'portable voice format'],
	[0, 'beshort', '=', 520, 'mc68k COFF'],
	[0, 'beshort', '=', 521, 'mc68k executable (shared)'],
	[0, 'beshort', '=', 522, 'mc68k executable (shared demand paged)'],
	[0, 'beshort', '=', 554, '68K BCS executable'],
	[0, 'beshort', '=', 555, '88K BCS executable'],
	[0, 'string', '=', 'S0', 'Motorola S-Record; binary data in text format'],
	[0, 'string', '=', '@echo off', 'MS-DOS batch file text'],
	[128, 'string', '=', 'PE\000\000', 'MS Windows PE'],
	[0, 'leshort', '=', 332, 'MS Windows COFF Intel 80386 object file'],
	[0, 'leshort', '=', 358, 'MS Windows COFF MIPS R4000 object file'],
	[0, 'leshort', '=', 388, 'MS Windows COFF Alpha object file'],
	[0, 'leshort', '=', 616, 'MS Windows COFF Motorola 68000 object file'],
	[0, 'leshort', '=', 496, 'MS Windows COFF PowerPC object file'],
	[0, 'leshort', '=', 656, 'MS Windows COFF PA-RISC object file'],
	[0, 'string', '=', 'MZ', 'application/x-ms-dos-executable'],
	[0, 'string', '=', 'LZ', 'MS-DOS executable (built-in)'],
	[0, 'string', '=', 'regf', 'Windows NT Registry file'],
	[2080, 'string', '=', 'Microsoft Word 6.0 Document', 'text/vnd.ms-word'],
	[2080, 'string', '=', 'Documento Microsoft Word 6', 'text/vnd.ms-word'],
	[2112, 'string', '=', 'MSWordDoc', 'text/vnd.ms-word'],
	[0, 'belong', '=', 834535424, 'text/vnd.ms-word'],
	[0, 'string', '=', 'PO^Q`', 'text/vnd.ms-word'],
	[2080, 'string', '=', 'Microsoft Excel 5.0 Worksheet', 'application/vnd.ms-excel'],
	[2114, 'string', '=', 'Biff5', 'application/vnd.ms-excel'],
	[0, 'belong', '=', 6656, 'Lotus 1-2-3'],
	[0, 'belong', '=', 512, 'Lotus 1-2-3'],
	[1, 'string', '=', 'WPC', 'text/vnd.wordperfect'],
	[0, 'beshort', '=', 610, 'Tower/XP rel 2 object'],
	[0, 'beshort', '=', 615, 'Tower/XP rel 2 object'],
	[0, 'beshort', '=', 620, 'Tower/XP rel 3 object'],
	[0, 'beshort', '=', 625, 'Tower/XP rel 3 object'],
	[0, 'beshort', '=', 630, 'Tower32/600/400 68020 object'],
	[0, 'beshort', '=', 640, 'Tower32/800 68020'],
	[0, 'beshort', '=', 645, 'Tower32/800 68010'],
	[0, 'lelong', '=', 407, 'NetBSD little-endian object file'],
	[0, 'belong', '=', 407, 'NetBSD big-endian object file'],
	[0, 'belong&0377777777', '=', 41400413, 'NetBSD/i386 demand paged'],
	[0, 'belong&0377777777', '=', 41400410, 'NetBSD/i386 pure'],
	[0, 'belong&0377777777', '=', 41400407, 'NetBSD/i386'],
	[0, 'belong&0377777777', '=', 41400507, 'NetBSD/i386 core'],
	[0, 'belong&0377777777', '=', 41600413, 'NetBSD/m68k demand paged'],
	[0, 'belong&0377777777', '=', 41600410, 'NetBSD/m68k pure'],
	[0, 'belong&0377777777', '=', 41600407, 'NetBSD/m68k'],
	[0, 'belong&0377777777', '=', 41600507, 'NetBSD/m68k core'],
	[0, 'belong&0377777777', '=', 42000413, 'NetBSD/m68k4k demand paged'],
	[0, 'belong&0377777777', '=', 42000410, 'NetBSD/m68k4k pure'],
	[0, 'belong&0377777777', '=', 42000407, 'NetBSD/m68k4k'],
	[0, 'belong&0377777777', '=', 42000507, 'NetBSD/m68k4k core'],
	[0, 'belong&0377777777', '=', 42200413, 'NetBSD/ns32532 demand paged'],
	[0, 'belong&0377777777', '=', 42200410, 'NetBSD/ns32532 pure'],
	[0, 'belong&0377777777', '=', 42200407, 'NetBSD/ns32532'],
	[0, 'belong&0377777777', '=', 42200507, 'NetBSD/ns32532 core'],
	[0, 'belong&0377777777', '=', 42400413, 'NetBSD/sparc demand paged'],
	[0, 'belong&0377777777', '=', 42400410, 'NetBSD/sparc pure'],
	[0, 'belong&0377777777', '=', 42400407, 'NetBSD/sparc'],
	[0, 'belong&0377777777', '=', 42400507, 'NetBSD/sparc core'],
	[0, 'belong&0377777777', '=', 42600413, 'NetBSD/pmax demand paged'],
	[0, 'belong&0377777777', '=', 42600410, 'NetBSD/pmax pure'],
	[0, 'belong&0377777777', '=', 42600407, 'NetBSD/pmax'],
	[0, 'belong&0377777777', '=', 42600507, 'NetBSD/pmax core'],
	[0, 'belong&0377777777', '=', 43000413, 'NetBSD/vax demand paged'],
	[0, 'belong&0377777777', '=', 43000410, 'NetBSD/vax pure'],
	[0, 'belong&0377777777', '=', 43000407, 'NetBSD/vax'],
	[0, 'belong&0377777777', '=', 43000507, 'NetBSD/vax core'],
	[0, 'lelong', '=', 459141, 'ECOFF NetBSD/alpha binary'],
	[0, 'belong&0377777777', '=', 43200507, 'NetBSD/alpha core'],
	[0, 'belong&0377777777', '=', 43400413, 'NetBSD/mips demand paged'],
	[0, 'belong&0377777777', '=', 43400410, 'NetBSD/mips pure'],
	[0, 'belong&0377777777', '=', 43400407, 'NetBSD/mips'],
	[0, 'belong&0377777777', '=', 43400507, 'NetBSD/mips core'],
	[0, 'belong&0377777777', '=', 43600413, 'NetBSD/arm32 demand paged'],
	[0, 'belong&0377777777', '=', 43600410, 'NetBSD/arm32 pure'],
	[0, 'belong&0377777777', '=', 43600407, 'NetBSD/arm32'],
	[0, 'belong&0377777777', '=', 43600507, 'NetBSD/arm32 core'],
	[0, 'string', '=', 'StartFontMetrics', 'font/x-sunos-news'],
	[0, 'string', '=', 'StartFont', 'font/x-sunos-news'],
	[0, 'belong', '=', 326773060, 'font/x-sunos-news'],
	[0, 'belong', '=', 326773063, 'font/x-sunos-news'],
	[0, 'belong', '=', 326773072, 'font/x-sunos-news'],
	[0, 'belong', '=', 326773073, 'font/x-sunos-news'],
	[8, 'belong', '=', 326773573, 'font/x-sunos-news'],
	[8, 'belong', '=', 326773576, 'font/x-sunos-news'],
	[0, 'string', '=', 'Octave-1-L', 'Octave binary data (little endian)'],
	[0, 'string', '=', 'Octave-1-B', 'Octave binary data (big endian)'],
	[0, 'string', '=', '\177OLF', 'OLF'],
	[0, 'beshort', '=', 34765, 'OS9/6809 module:'],
	[0, 'beshort', '=', 19196, 'OS9/68K module:'],
	[0, 'long', '=', 61374, 'OSF/Rose object'],
	[0, 'short', '=', 565, 'i386 COFF object'],
	[0, 'short', '=', 10775, '"compact bitmap" format (Poskanzer)'],
	[0, 'string', '=', '%PDF-', 'PDF document'],
	[0, 'lelong', '=', 101555, 'PDP-11 single precision APL workspace'],
	[0, 'lelong', '=', 101554, 'PDP-11 double precision APL workspace'],
	[0, 'leshort', '=', 407, 'PDP-11 executable'],
	[0, 'leshort', '=', 401, 'PDP-11 UNIX/RT ldp'],
	[0, 'leshort', '=', 405, 'PDP-11 old overlay'],
	[0, 'leshort', '=', 410, 'PDP-11 pure executable'],
	[0, 'leshort', '=', 411, 'PDP-11 separate I&D executable'],
	[0, 'leshort', '=', 437, 'PDP-11 kernel overlay'],
	[0, 'beshort', '=', 39168, 'PGP key public ring'],
	[0, 'beshort', '=', 38145, 'PGP key security ring'],
	[0, 'beshort', '=', 38144, 'PGP key security ring'],
	[0, 'beshort', '=', 42496, 'PGP encrypted data'],
	[0, 'string', '=', '-----BEGIN PGP', 'PGP armored data'],
	[0, 'string', '=', '# PaCkAgE DaTaStReAm', 'pkg Datastream (SVR4)'],
	[0, 'short', '=', 601, 'mumps avl global'],
	[0, 'short', '=', 602, 'mumps blt global'],
	[0, 'string', '=', '%!', 'application/postscript'],
	[0, 'string', '=', '\004%!', 'application/postscript'],
	[0, 'belong', '=', 3318797254, 'DOS EPS Binary File'],
	[0, 'string', '=', '*PPD-Adobe:', 'PPD file'],
	[0, 'string', '=', '\033%-12345X@PJL', 'HP Printer Job Language data'],
	[0, 'string', '=', '\033%-12345X@PJL', 'HP Printer Job Language data'],
	[0, 'string', '=', '\033E\033', 'image/x-pcl-hp'],
	[0, 'string', '=', '@document(', 'Imagen printer'],
	[0, 'string', '=', 'Rast', 'RST-format raster font data'],
	[0, 'belong&0xff00ffff', '=', 1442840576, 'ps database'],
	[0, 'long', '=', 1351614727, 'Pyramid 90x family executable'],
	[0, 'long', '=', 1351614728, 'Pyramid 90x family pure executable'],
	[0, 'long', '=', 1351614731, 'Pyramid 90x family demand paged pure executable'],
	[0, 'beshort', '=', 60843, ''],
	[0, 'string', '=', '{\\\\rtf', 'Rich Text Format data,'],
	[38, 'string', '=', 'Spreadsheet', 'sc spreadsheet file'],
	[8, 'string', '=', '\001s SCCS', 'archive data'],
	[0, 'byte', '=', 46, 'Sendmail frozen configuration'],
	[0, 'short', '=', 10012, 'Sendmail frozen configuration'],
	[0, 'lelong', '=', 234, 'BALANCE NS32000 .o'],
	[0, 'lelong', '=', 4330, 'BALANCE NS32000 executable (0 @ 0)'],
	[0, 'lelong', '=', 8426, 'BALANCE NS32000 executable (invalid @ 0)'],
	[0, 'lelong', '=', 12522, 'BALANCE NS32000 standalone executable'],
	[0, 'leshort', '=', 4843, 'SYMMETRY i386 .o'],
	[0, 'leshort', '=', 8939, 'SYMMETRY i386 executable (0 @ 0)'],
	[0, 'leshort', '=', 13035, 'SYMMETRY i386 executable (invalid @ 0)'],
	[0, 'leshort', '=', 17131, 'SYMMETRY i386 standalone executable'],
	[0, 'string', '=', 'kbd!map', 'kbd map file'],
	[0, 'belong', '=', 407, 'old SGI 68020 executable'],
	[0, 'belong', '=', 410, 'old SGI 68020 pure executable'],
	[0, 'beshort', '=', 34661, 'disk quotas file'],
	[0, 'beshort', '=', 1286, 'IRIS Showcase file'],
	[0, 'beshort', '=', 550, 'IRIS Showcase template'],
	[0, 'belong', '=', 1396917837, 'IRIS Showcase file'],
	[0, 'belong', '=', 1413695053, 'IRIS Showcase template'],
	[0, 'belong', '=', 3735927486, 'IRIX Parallel Arena'],
	[0, 'beshort', '=', 352, 'MIPSEB COFF executable'],
	[0, 'beshort', '=', 354, 'MIPSEL COFF executable'],
	[0, 'beshort', '=', 24577, 'MIPSEB-LE COFF executable'],
	[0, 'beshort', '=', 25089, 'MIPSEL-LE COFF executable'],
	[0, 'beshort', '=', 355, 'MIPSEB MIPS-II COFF executable'],
	[0, 'beshort', '=', 358, 'MIPSEL MIPS-II COFF executable'],
	[0, 'beshort', '=', 25345, 'MIPSEB-LE MIPS-II COFF executable'],
	[0, 'beshort', '=', 26113, 'MIPSEL-LE MIPS-II COFF executable'],
	[0, 'beshort', '=', 320, 'MIPSEB MIPS-III COFF executable'],
	[0, 'beshort', '=', 322, 'MIPSEL MIPS-III COFF executable'],
	[0, 'beshort', '=', 16385, 'MIPSEB-LE MIPS-III COFF executable'],
	[0, 'beshort', '=', 16897, 'MIPSEL-LE MIPS-III COFF executable'],
	[0, 'beshort', '=', 384, 'MIPSEB Ucode'],
	[0, 'beshort', '=', 386, 'MIPSEL Ucode'],
	[0, 'belong', '=', 3735924144, 'IRIX core dump'],
	[0, 'belong', '=', 3735924032, 'IRIX 64-bit core dump'],
	[0, 'belong', '=', 3133063355, 'IRIX N32 core dump'],
	[0, 'string', '=', 'CrshDump', 'IRIX vmcore dump of'],
	[0, 'string', '=', 'SGIAUDIT', 'SGI Audit file'],
	[0, 'string', '=', 'WNGZWZSC', 'Wingz compiled script'],
	[0, 'string', '=', 'WNGZWZSS', 'Wingz spreadsheet'],
	[0, 'string', '=', 'WNGZWZHP', 'Wingz help file'],
	[0, 'string', '=', '\\#Inventor', 'V IRIS Inventor 1.0 file'],
	[0, 'string', '=', '\\#Inventor', 'V2 Open Inventor 2.0 file'],
	[0, 'string', '=', 'glfHeadMagic();', 'GLF_TEXT'],
	[4, 'belong', '=', 1090584576, 'GLF_BINARY_LSB_FIRST'],
	[4, 'belong', '=', 321, 'GLF_BINARY_MSB_FIRST'],
	[0, 'string', '=', '<!DOCTYPE HTML', 'text/html'],
	[0, 'string', '=', '<!doctype html', 'text/html'],
	[0, 'string', '=', '<HEAD', 'text/html'],
	[0, 'string', '=', '<head', 'text/html'],
	[0, 'string', '=', '<TITLE', 'text/html'],
	[0, 'string', '=', '<title', 'text/html'],
	[0, 'string', '=', '<html', 'text/html'],
	[0, 'string', '=', '<HTML', 'text/html'],
	[0, 'string', '=', '<!DOCTYPE', 'exported SGML document text'],
	[0, 'string', '=', '<!doctype', 'exported SGML document text'],
	[0, 'string', '=', '<!SUBDOC', 'exported SGML subdocument text'],
	[0, 'string', '=', '<!subdoc', 'exported SGML subdocument text'],
	[0, 'string', '=', '<!--', 'exported SGML document text'],
	[0, 'string', '=', 'RTSS', 'NetMon capture file'],
	[0, 'string', '=', 'TRSNIFF data    \032', 'Sniffer capture file'],
	[0, 'string', '=', 'XCP\000', 'NetXRay capture file'],
	[0, 'ubelong', '=', 2712847316, 'tcpdump capture file (big-endian)'],
	[0, 'ulelong', '=', 2712847316, 'tcpdump capture file (little-endian)'],
	[0, 'string', '=', '<!SQ DTD>', 'Compiled SGML rules file'],
	[0, 'string', '=', '<!SQ A/E>', 'A/E SGML Document binary'],
	[0, 'string', '=', '<!SQ STS>', 'A/E SGML binary styles file'],
	[0, 'short', '=', 49374, 'Compiled PSI (v1) data'],
	[0, 'short', '=', 49370, 'Compiled PSI (v2) data'],
	[0, 'short', '=', 125252, 'SoftQuad DESC or font file binary'],
	[0, 'string', '=', 'SQ BITMAP1', 'SoftQuad Raster Format text'],
	[0, 'string', '=', 'X SoftQuad', 'troff Context intermediate'],
	[0, 'belong&077777777', '=', 600413, 'sparc demand paged'],
	[0, 'belong&077777777', '=', 600410, 'sparc pure'],
	[0, 'belong&077777777', '=', 600407, 'sparc'],
	[0, 'belong&077777777', '=', 400413, 'mc68020 demand paged'],
	[0, 'belong&077777777', '=', 400410, 'mc68020 pure'],
	[0, 'belong&077777777', '=', 400407, 'mc68020'],
	[0, 'belong&077777777', '=', 200413, 'mc68010 demand paged'],
	[0, 'belong&077777777', '=', 200410, 'mc68010 pure'],
	[0, 'belong&077777777', '=', 200407, 'mc68010'],
	[0, 'belong', '=', 407, 'old sun-2 executable'],
	[0, 'belong', '=', 410, 'old sun-2 pure executable'],
	[0, 'belong', '=', 413, 'old sun-2 demand paged executable'],
	[0, 'belong', '=', 525398, 'SunOS core file'],
	[0, 'long', '=', 4197695630, 'SunPC 4.0 Hard Disk'],
	[0, 'string', '=', '#SUNPC_CONFIG', 'SunPC 4.0 Properties Values'],
	[0, 'string', '=', 'snoop', 'Snoop capture file'],
	[36, 'string', '=', 'acsp', 'Kodak Color Management System, ICC Profile'],
	[0, 'string', '=', '#!teapot\012xdr', 'teapot work sheet (XDR format)'],
	[0, 'string', '=', '\032\001', 'Compiled terminfo entry'],
	[0, 'short', '=', 433, 'Curses screen image'],
	[0, 'short', '=', 434, 'Curses screen image'],
	[0, 'string', '=', '\367\002', 'TeX DVI file'],
	[0, 'string', '=', '\367\203', 'font/x-tex'],
	[0, 'string', '=', '\367Y', 'font/x-tex'],
	[0, 'string', '=', '\367\312', 'font/x-tex'],
	[0, 'string', '=', 'This is TeX,', 'TeX transcript text'],
	[0, 'string', '=', 'This is METAFONT,', 'METAFONT transcript text'],
	[2, 'string', '=', '\000\021', 'font/x-tex-tfm'],
	[2, 'string', '=', '\000\022', 'font/x-tex-tfm'],
	[0, 'string', '=', '\\\\input\\', 'texinfo Texinfo source text'],
	[0, 'string', '=', 'This is Info file', 'GNU Info text'],
	[0, 'string', '=', '\\\\input', 'TeX document text'],
	[0, 'string', '=', '\\\\section', 'LaTeX document text'],
	[0, 'string', '=', '\\\\setlength', 'LaTeX document text'],
	[0, 'string', '=', '\\\\documentstyle', 'LaTeX document text'],
	[0, 'string', '=', '\\\\chapter', 'LaTeX document text'],
	[0, 'string', '=', '\\\\documentclass', 'LaTeX 2e document text'],
	[0, 'string', '=', '\\\\relax', 'LaTeX auxiliary file'],
	[0, 'string', '=', '\\\\contentsline', 'LaTeX table of contents'],
	[0, 'string', '=', '\\\\indexentry', 'LaTeX raw index file'],
	[0, 'string', '=', '\\\\begin{theindex}', 'LaTeX sorted index'],
	[0, 'string', '=', '\\\\glossaryentry', 'LaTeX raw glossary'],
	[0, 'string', '=', '\\\\begin{theglossary}', 'LaTeX sorted glossary'],
	[0, 'string', '=', 'This is makeindex', 'Makeindex log file'],
	[0, 'string', '=', '**TI82**', 'TI-82 Graphing Calculator'],
	[0, 'string', '=', '**TI83**', 'TI-83 Graphing Calculator'],
	[0, 'string', '=', '**TI85**', 'TI-85 Graphing Calculator'],
	[0, 'string', '=', '**TI92**', 'TI-92 Graphing Calculator'],
	[0, 'string', '=', '**TI80**', 'TI-80 Graphing Calculator File.'],
	[0, 'string', '=', '**TI81**', 'TI-81 Graphing Calculator File.'],
	[0, 'string', '=', 'TZif', 'timezone data'],
	[0, 'string', '=', '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\001\000', 'old timezone data'],
	[0, 'string', '=', '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\002\000', 'old timezone data'],
	[0, 'string', '=', '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\003\000', 'old timezone data'],
	[0, 'string', '=', '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\004\000', 'old timezone data'],
	[0, 'string', '=', '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\005\000', 'old timezone data'],
	[0, 'string', '=', '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\006\000', 'old timezone data'],
	[0, 'string', '=', '.\\\\"', 'troff or preprocessor input text'],
	[0, 'string', '=', '\'\\\\"', 'troff or preprocessor input text'],
	[0, 'string', '=', '\'.\\\\"', 'troff or preprocessor input text'],
	[0, 'string', '=', '\\\\"', 'troff or preprocessor input text'],
	[0, 'string', '=', 'x T', 'ditroff text'],
	[0, 'string', '=', '@\357', 'very old (C/A/T) troff output data'],
	[0, 'string', '=', 'Interpress/Xerox', 'Xerox InterPress data'],
	[0, 'short', '=', 263, 'unknown machine executable'],
	[0, 'short', '=', 264, 'unknown pure executable'],
	[0, 'short', '=', 265, 'PDP-11 separate I&D'],
	[0, 'short', '=', 267, 'unknown pure executable'],
	[0, 'long', '=', 268, 'unknown demand paged pure executable'],
	[0, 'long', '=', 269, 'unknown demand paged pure executable'],
	[0, 'long', '=', 270, 'unknown readable demand paged pure executable'],
	[0, 'string', '=', 'begin uuencoded', 'or xxencoded text'],
	[0, 'string', '=', 'xbtoa Begin', "btoa'd text"],
	[0, 'string', '=', '$\012ship', "ship'd binary text"],
	[0, 'string', '=', 'Decode the following with bdeco', 'bencoded News text'],
	[11, 'string', '=', 'must be converted with BinHex', 'BinHex binary text'],
	[0, 'short', '=', 610, 'Perkin-Elmer executable'],
	[0, 'beshort', '=', 572, 'amd 29k coff noprebar executable'],
	[0, 'beshort', '=', 1572, 'amd 29k coff prebar executable'],
	[0, 'beshort', '=', 160007, 'amd 29k coff archive'],
	[6, 'beshort', '=', 407, 'unicos (cray) executable'],
	[596, 'string', '=', 'X\337\377\377', 'Ultrix core file'],
	[0, 'string', '=', 'Joy!peffpwpc', 'header for PowerPC PEF executable'],
	[0, 'lelong', '=', 101557, 'VAX single precision APL workspace'],
	[0, 'lelong', '=', 101556, 'VAX double precision APL workspace'],
	[0, 'lelong', '=', 407, 'VAX executable'],
	[0, 'lelong', '=', 410, 'VAX pure executable'],
	[0, 'lelong', '=', 413, 'VAX demand paged pure executable'],
	[0, 'leshort', '=', 570, 'VAX COFF executable'],
	[0, 'leshort', '=', 575, 'VAX COFF pure executable'],
	[0, 'string', '=', 'LBLSIZE=', 'VICAR image data'],
	[43, 'string', '=', 'SFDU_LABEL', 'VICAR label file'],
	[0, 'short', '=', 21845, 'VISX image file'],
	[0, 'string', '=', '\260\0000\000', 'VMS VAX executable'],
	[0, 'belong', '=', 50331648, 'VMS Alpha executable'],
	[1, 'string', '=', 'WPC', '(Corel/WP)'],
	[0, 'string', '=', 'core', 'core file (Xenix)'],
	[0, 'byte', '=', 128, '8086 relocatable (Microsoft)'],
	[0, 'leshort', '=', 65381, 'x.out'],
	[0, 'leshort', '=', 518, 'Microsoft a.out'],
	[0, 'leshort', '=', 320, 'old Microsoft 8086 x.out'],
	[0, 'lelong', '=', 518, 'b.out'],
	[0, 'leshort', '=', 1408, 'XENIX 8086 relocatable or 80286 small model'],
	[0, 'long', '=', 59399, 'object file (z8000 a.out)'],
	[0, 'long', '=', 59400, 'pure object file (z8000 a.out)'],
	[0, 'long', '=', 59401, 'separate object file (z8000 a.out)'],
	[0, 'long', '=', 59397, 'overlay object file (z8000 a.out)'],
	[0, 'string', '=', 'ZyXEL\002', 'ZyXEL voice data'],
]
#=================================================================
magicNumbers = []

def strToNum(n):
	val = 0
	col = int(1)
	if n[:1] == 'x': n = '0' + n
	if n[:2] == '0x':
		# hex
		n = n[2:].lower()
		while len(n) > 0:
			l = n[len(n) - 1]
			val = val + string.hexdigits.index(l) * col
			col = col * 16
			n = n[:len(n)-1]
	elif n[0] == '\\':
		# octal
		n = n[1:]
		while len(n) > 0:
			l = n[len(n) - 1]
			if ord(l) < 48 or ord(l) > 57: break
			val = val + int(l) * col
			col = col * 8
			n = n[:len(n)-1]
	else:
		val = int(n)
	return val

def unescape(s):
	# replace string escape sequences
	while 1:
		m = re.search(r'\\', s)
		if not m: break
		x = m.start()+1
		if m.end() == len(s): 
			# escaped space at end
			s = s[:len(s)-1] + ' '
		elif s[x:x+2] == '0x':
			# hex ascii value
			c = chr(strToNum(s[x:x+4]))
			s = s[:x-1] + c + s[x+4:]
		elif s[m.start()+1] == 'x':
			# hex ascii value
			c = chr(strToNum(s[x:x+3]))
			s = s[:x-1] + c + s[x+3:]
		elif ord(s[x]) > 47 and ord(s[x]) < 58:
			# octal ascii value
			end = x
			while (ord(s[end]) > 47 and ord(s[end]) < 58):
				end = end + 1
				if end > len(s) - 1: break
			c = chr(strToNum(s[x-1:end]))
			s = s[:x-1] + c + s[end:]
		elif s[x] == 'n':
			# newline
			s = s[:x-1] + '\n' + s[x+1:]
		else:
			break
	return s

class magicTest:
	def __init__(self, offset, t, op, value, msg, mask = None):
		if t.count('&') > 0:
			mask = strToNum(t[t.index('&')+1:])  
			t = t[:t.index('&')]
		if type(offset) == type('a'):
			self.offset = strToNum(offset)
		else:
			self.offset = offset
		self.type = t
		self.msg = msg
		self.subTests = []
		self.op = op
		self.mask = mask
		self.value = value

	def test(self, data):
		if self.mask:
			data = data & self.mask
		if self.op == '=': 
			if self.value == data: return self.msg
		elif self.op ==  '<':
			pass
		elif self.op ==  '>':
			pass
		elif self.op ==  '&':
			pass
		elif self.op ==  '^':
			pass
		return None

	def compare(self, data):
		#print str([self.type, self.value, self.msg])
		try: 
			if self.type == 'string':
				c = ''; s = ''
				for i in range(0, len(self.value)+1):
					if (i + self.offset) > (len(data) - 1): break
					s = s + c
					[c] = struct.unpack('c', data[self.offset + i])
				data = s
			elif self.type == 'short':
				[data] = struct.unpack('h', data[self.offset : self.offset + 2])
			elif self.type == 'leshort':
				[data] = struct.unpack('<h', data[self.offset : self.offset + 2])
			elif self.type == 'beshort':
				[data] = struct.unpack('>H', data[self.offset : self.offset + 2])
			elif self.type == 'long':
				[data] = struct.unpack('l', data[self.offset : self.offset + 4])
			elif self.type == 'lelong':
				[data] = struct.unpack('<l', data[self.offset : self.offset + 4])
			elif self.type == 'belong':
				[data] = struct.unpack('>l', data[self.offset : self.offset + 4])
			else:
				#print('UNKNOWN TYPE: ' + self.type)
				pass
		except Exception:
			return None

#    print str([self.msg, self.value, data])
		return self.test(data)


def load(file):
	global magicNumbers
	lines = open(file, mode = 'rt', encoding = 'utf8')
	last = { 0: None }
	for line in lines:
		if re.match(r'\s*#', line):
			# comment
			continue
		else:
			# split up by space delimiters, and remove trailing space
			line = line.rstrip()
			line = re.split(r'\s*', line)
			if len(line) < 3:
				# bad line
				continue
			offset = line[0]
			type = line[1]
			value = line[2]
			level = 0
			while offset[0] == '>':
				# count the level of the type
				level = level + 1
				offset = offset[1:]
			l = magicNumbers
			if level > 0:
				l = last[level - 1].subTests
			if offset[0] == '(':
				# don't handle indirect offsets just yet
				print('SKIPPING ' + ' '.join(list(line[3:])))
				pass
			elif offset[0] == '&':
				# don't handle relative offsets just yet
				print('SKIPPING ' + ' '.join(list(line[3:])))
				pass
			else:
				operands = ['=', '<', '>', '&']
				if operands.count(value[0]) > 0:
					# a comparison operator is specified
					op = value[0] 
					value = value[1:]
				else:
					print(str([value, operands]))
					if len(value) >1 and value[0] == '\\' and operands.count(value[1]) >0:
						# literal value that collides with operands is escaped
						value = value[1:]
					op = '='

				mask = None
				if type == 'string':
					while 1:
						value = unescape(value)
						if value[len(value)-1] == ' ' and len(line) > 3:
							# last value was an escaped space, join
							value = value + line[3]
							del line[3]
						else:
							break
				else:
					if value.count('&') != 0:
						mask = value[(value.index('&') + 1):]
						print('MASK: ' + mask)
						value = value[:(value.index('&')+1)]
					try: value = strToNum(value)
					except Exception: continue
					msg = ' '.join(list(line[3:]))
				new = magicTest(offset, type, op, value, msg, mask)
				last[level] = new
				l.append(new)



def whatis(data):
	for test in magicNumbers:
		 m = test.compare(data)
		 if m: return m
	# no matching, magic number. is it binary or text?
	for c in data:
		if ord(c) > 128:
			return 'data'
	# its ASCII, now do text tests
	if data.find('The', 0, 8192) > -1:
		return 'English text'
	if data.find('def', 0, 8192) > -1:
		return 'Python Source'
	return 'ASCII text'




def filedesc(file):
	try:
		return whatis(open(file, 'r').read(8192))
	except Exception as e:
		if str(e) == '[Errno 21] Is a directory':
			return 'directory'
		else:
			raise e

#### BUILD DATA ####
#load('mime-magic')
#f = open('out', mode = 'wt', encoding = 'utf8')
#for m in magicNumbers:
#  f.write(str([m.offset, m.type, m.op, m.value, m.msg]) + ',\n')
#f.close

for m in magic:
	magicNumbers.append(magicTest(m[0], m[1], m[2], m[3], m[4]))

#=================================================================
if __name__ == '__main__':
	import sys
	for arg in sys.argv[1:]:
		msg = open(arg)
		if msg:
			print(arg + ': ' + msg)
		else:
			print(arg + ': unknown')
#=================================================================
