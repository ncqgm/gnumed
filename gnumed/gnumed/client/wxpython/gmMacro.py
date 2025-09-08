# -*- coding: utf-8 -*-
"""GNUmed macro primitives.

This module implements functions a macro can legally use.
"""
#=====================================================================
__author__ = "K.Hilbert <karsten.hilbert@gmx.net>"

import sys
import random
import logging
import os
import datetime
import urllib.parse
import codecs
import re as regex


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmBorg
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmCfgINI
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmMimeLib
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmCrypto
from Gnumed.pycommon import gmDispatcher

from Gnumed.business import gmPerson
from Gnumed.business import gmGender
from Gnumed.business import gmStaff
from Gnumed.business import gmMedication
from Gnumed.business import gmPathLab
from Gnumed.business import gmPersonSearch
from Gnumed.business import gmVaccination
from Gnumed.business import gmKeywordExpansion
from Gnumed.business import gmPraxis

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmNarrativeWorkflows
from Gnumed.wxpython import gmPatSearchWidgets
from Gnumed.wxpython import gmPersonContactWidgets
from Gnumed.wxpython import gmEMRStructWidgets
from Gnumed.wxpython import gmEncounterWidgets
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmDemographicsWidgets
from Gnumed.wxpython import gmDocumentWidgets
from Gnumed.wxpython import gmKeywordExpansionWidgets
from Gnumed.wxpython import gmPraxisWidgets
from Gnumed.wxpython import gmAddressWidgets


_log = logging.getLogger('gm.scripting')
_cfg = gmCfgINI.gmCfgData()

#=====================================================================
# values for the following placeholders must be injected from the outside before
# using them, in use they must conform to the "placeholder::::max length" syntax,
# as long as they resolve to None they return their respective names so the
# developers can know which placeholder was not set
known_injectable_placeholders = [
	'form_name_long',
	'form_name_short',
	'form_version',
	'form_version_internal',
	'form_last_modified'
]

# the following must satisfy the pattern "$<name::args::(optional) max string length>$" when used
__known_variant_placeholders = {
	# generic:
	'free_text': u"""show a dialog for entering some free text:
		args: <message>//<preset>
			<message>: shown in input dialog, must not contain either
				of '::' and whatever the arguments divider is
				set to (default '//'),
			<preset>: whatever to initially show inside the input field,
		caches input per <message>""",

	'text_snippet': """a text snippet, taken from the keyword expansion mechanism:
		args: <snippet name>//<template>""",

	'data_snippet': """a binary snippet, taken from the keyword expansion mechanism:
		args: <snippet name>//<template>//<optional target mime type>//<optional target extension>
		returns full path to an exported copy of the
		data rather than the data itself,
		template: string template for outputting the path
		target mime type: a mime type into which to convert the image, no conversion if not given
		target extension: target file name extension, derived from target mime type if not given
	""",
	u'qrcode': u"""generate QR code file for a text snippet:
		returns: path to QR code png file
		args: <text>//<template>
			text: utf8 text, will always be encoded in 'binary' mode with utf8 as encoding
			template: %s-template into which to insert the QR code png file path
	""",

	# control flow
	'yes_no': """Ask user a yes-no question and return content based on answer.
		args: msg=<message>//yes=<yes>//no=<no>
			<message>: shown in the yes/no dialog presented to the user
			<yes>: returned if the user selects "yes"
			<no>: returned if the user selects "no"
	""",

	# text manipulation
	'range_of': """select range of enclosed text (note that this cannot take into account non-length characters such as enclosed LaTeX code
		args: <enclosed text>
	""",
	'if_not_empty': """format text based on template if not empty
		args: <possibly-empty-text>//<template-if-not-empty>//<alternative-text-if-empty>
	""",

	u'tex_escape': u"args: string to escape, mostly obsolete now",

	u'url_escape': u"""Escapes a string suitable for use as _data_ in an URL
		args: text to escape
	""",

	# internal state
	'ph_cfg': u"""Set placeholder handler options.
		args: option name//option value//macro return string
		option names:
			ellipsis: what to use as ellipsis (if anything) when
				shortening strings or string regions, setting the
				value to NONE will switch off ellipis handling,
				default is switched off
			argumentsdivider: what to use as divider when splitting
				an argument string into parts, default is '//',
				note that the 'config' placeholder will ALWAYS
				use '//' to split its argument string, regardless
				of which setting of <argumentsdivider> is in effect,
				use DEFAULT to reset this setting back to the
				default '//'
			encoding: the encoding in which data emitted by GNUmed
				as placeholder replacement needs to be valid in,
				note that GNUmed will still emit unicode to replacement
				consumers but it will ensure the data emitted _can_
				be encoded by this target encoding (by roundtripping
				unicode-encoding-unicode)
				valid from where this placeholder is located at
				until further change,
				use DEFAULT to reset encoding back to the default
				which is to not ensure compatibility,
				if the encoding ends in '-strict' then the placeholder
				replacement will fail if the roundtrip fails
	""",
	u'if_debugging': u"""set text based on whether debugging is active
		args: <text-if-debugging>//<text-if-not-debugging>
	""",

	'today': "args: strftime format",

	'gender_mapper': """maps gender of patient to a string:
		args: <value when person is male> // <is female> // <is other>
		eg. 'male//female//other'
		or: 'Lieber Patient//Liebe Patientin'""",
	'client_version': "the version of the current client as a string (no 'v' in front)",

	'gen_adr_street': """part of a generic address, cached, selected from database:
		args: optional template//optional selection message//optional cache ID
		template: %s-style formatting template
		message: text message shown in address selection list
		cache ID: used to differentiate separate cached invocations of this placeholder
	""",
	'gen_adr_number': """part of a generic address, cached, selected from database:
		args: optional template//optional selection message//optional cache ID
		template: %s-style formatting template
		message: text message shown in address selection list
		cache ID: used to differentiate separate cached invocations of this placeholder
	""",
	'gen_adr_subunit': """part of a generic address, cached, selected from database:
		args: optional template//optional selection message//optional cache ID
		template: %s-style formatting template
		message: text message shown in address selection list
		cache ID: used to differentiate separate cached invocations of this placeholder
	""",
	'gen_adr_location': """part of a generic address, cached, selected from database:
		args: optional template//optional selection message//optional cache ID
		template: %s-style formatting template
		message: text message shown in address selection list
		cache ID: used to differentiate separate cached invocations of this placeholder
	""",
	'gen_adr_suburb': """part of a generic address, cached, selected from database:
		args: optional template//optional selection message//optional cache ID
		template: %s-style formatting template
		message: text message shown in address selection list
		cache ID: used to differentiate separate cached invocations of this placeholder
	""",
	'gen_adr_postcode': """part of a generic address, cached, selected from database:
		args: optional template//optional selection message//optional cache ID
		template: %s-style formatting template
		message: text message shown in address selection list
		cache ID: used to differentiate separate cached invocations of this placeholder
	""",
	'gen_adr_region': """part of a generic address, cached, selected from database:
		args: optional template//optional selection message//optional cache ID
		template: %s-style formatting template
		message: text message shown in address selection list
		cache ID: used to differentiate separate cached invocations of this placeholder
	""",
	'gen_adr_country': """part of a generic address, cached, selected from database:
		args: optional template//optional selection message//optional cache ID
		template: %s-style formatting template
		message: text message shown in address selection list
		cache ID: used to differentiate separate cached invocations of this placeholder
	""",

	'receiver_name': """the receiver name, cached, selected from database:
		receivers are presented for selection from people/addresses related
		to the patient in some way or other,
		args: optional template//optional cache ID
		template: %s-style formatting template
		cache ID: used to differentiate separate cached invocations of this placeholder
	""",
	'receiver_street': """part of a receiver address, cached, selected from database:
		receivers are presented for selection from people/addresses related
		to the patient in some way or other,
		args: optional template//optional cache ID
		template: %s-style formatting template
		cache ID: used to differentiate separate cached invocations of this placeholder
	""",
	'receiver_number': """part of a receiver address, cached, selected from database:
		receivers are presented for selection from people/addresses related
		to the patient in some way or other,
		args: optional template//optional cache ID
		template: %s-style formatting template
		cache ID: used to differentiate separate cached invocations of this placeholder
	""",
	'receiver_subunit': """part of a receiver address, cached, selected from database:
		receivers are presented for selection from people/addresses related
		to the patient in some way or other,
		args: optional template//optional cache ID
		template: %s-style formatting template
		cache ID: used to differentiate separate cached invocations of this placeholder
	""",
	'receiver_location': """part of a receiver address, cached, selected from database:
		receivers are presented for selection from people/addresses related
		to the patient in some way or other,
		args: optional template//optional cache ID
		template: %s-style formatting template
		cache ID: used to differentiate separate cached invocations of this placeholder
	""",
	'receiver_suburb': """part of a receiver address, cached, selected from database:
		receivers are presented for selection from people/addresses related
		to the patient in some way or other,
		args: optional template//optional cache ID
		template: %s-style formatting template
		cache ID: used to differentiate separate cached invocations of this placeholder
	""",
	'receiver_postcode': """part of a receiver address, cached, selected from database:
		receivers are presented for selection from people/addresses related
		to the patient in some way or other,
		args: optional template//optional cache ID
		template: %s-style formatting template
		cache ID: used to differentiate separate cached invocations of this placeholder
	""",
	'receiver_region': """part of a receiver address, cached, selected from database:
		receivers are presented for selection from people/addresses related
		to the patient in some way or other,
		args: optional template//optional cache ID
		template: %s-style formatting template
		cache ID: used to differentiate separate cached invocations of this placeholder
	""",
	'receiver_country': """part of a receiver address, cached, selected from database:
		receivers are presented for selection from people/addresses related
		to the patient in some way or other,
		args: optional template//optional cache ID
		template: %s-style formatting template
		cache ID: used to differentiate separate cached invocations of this placeholder, if necessary
	""",

	# patient demographics:
	'name': "args: template for name parts arrangement",
	'date_of_birth': "args: strftime date/time format directive",

	'patient_address': """Return one patient address.
		Options:
			type: the type of address to use, asks user if empty
			fmt: if set to 'mapurl': return formatted as URL pointing to an online map
			tmpl: the formatting template, if <fmt> is not 'mapurl'
	""",
	'adr_street': "args: <type of address>, cached per type",
	'adr_number': "args: <type of address>, cached per type",
	'adr_subunit': "args: <type of address>, cached per type",
	'adr_location': "args: <type of address>, cached per type",
	'adr_suburb': "args: <type of address>, cached per type",
	'adr_postcode': "args: <type of address>, cached per type",
	'adr_region': "args: <type of address>, cached per type",
	'adr_country': "args: <type of address>, cached per type",

	'patient_comm': "args: <comm channel type as per database>//<%(field)s-template>",

	'patient_vcf': """returns path to VCF for current patient
		args: <template>
		template: %s-template for path
	""",
	'patient_gdt': """returns path to GDT for current patient
		args: <template>
		template: %s-template for path
	""",
	u'patient_mcf': u"""returns MECARD for current patient
		args: <format>//<template>
		format: fmt=qr|mcf|txt
			qr: QR code png file path,
			mcf: MECARD .mcf file path,
			txt: MECARD string,
			default - if omitted - is "txt",
		template: tmpl=<%s-template string>, "%s" if omitted
	""",

	'patient_tags': "args: <%(field)s-template>//<separator>",
	#u'patient_tags_table': u"no args",
	'patient_photo': """outputs URL to exported patient photo (cached per mime type and extension):
		args: <template>//<optional target mime type>//<optional target extension>,
		returns full path to an exported copy of the
		image rather than the image data itself,
		returns u'' if no mugshot available,
		template: string template for outputting the path
		target mime type: a mime type into which to convert the image, no conversion if not given
		target extension: target file name extension, derived from target mime type if not given""",
	'external_id': "args: <type of ID>//<issuer of ID>",


	# clinical record related:
	'soap': "get all of SOAPU/ADMIN, no template in args needed",
	'soap_s': "get subset of SOAPU/ADMIN, no template in args needed",
	'soap_o': "get subset of SOAPU/ADMIN, no template in args needed",
	'soap_a': "get subset of SOAPU/ADMIN, no template in args needed",
	'soap_p': "get subset of SOAPU/ADMIN, no template in args needed",
	'soap_u': "get subset of SOAPU/ADMIN, no template in args needed",
	'soap_admin': "get subset of SOAPU/ADMIN, no template in args needed",

	'progress_notes': """get progress notes:
		args: categories//template
		categories: string with 'soapu '; ' ' == None == admin
		template:	u'something %s something'		(do not include // in template !)""",

	'soap_for_encounters': """lets the user select a list of encounters for which:
		LaTeX formatted progress notes are emitted,
		args: soap categories // strftime date format""",

	'soap_by_issue': """lets the user select a list of issues and then SOAP entries from those issues:
		args: soap categories // strftime date format // template""",

	'soap_by_episode': """lets the user select a list of episodes and then SOAP entries from those episodes:
		args: soap categories // strftime date format // template""",

	'emr_journal': """returns EMR journal view entries:
		args format:   <categories>//<template>//<line length>//<time range>//<target format>
		categories:	   string with any of "s", "o", "a", "p", "u", " "; (" " == None == admin category)
		template:	   something %s something else (Do not include // in the template !)
		line length:   the maximum length of individual lines, not the total placeholder length
		time range:		the number of weeks going back in time if given as a single number, or else it must be a valid PostgreSQL interval definition (w/o the ::interval)""",

	'substance_abuse': """returns substance abuse entries:
		args: line template
	""",

	'current_meds': """returns current medications:
		args: line template//<select>
		<select>: if this is present the user will be asked which meds to export""",

	'current_meds_for_rx': """formats substance intakes either by substance (non-product intakes) or by producdt (once per product intake, even if multi-component):
		args: <line template>
		<line_template>: template into which to insert each intake, keys from
		clin.v_intakes__active, special additional keys:
			%(contains)s -- list of components
			%(amount2dispense)s -- how much/many to dispense""",

	'current_meds_AMTS': """emit LaTeX longtable lines with appropriate page breaks:
		also creates per-page AMTS QR codes and sets the
		following internal placeholders:
			amts_png_file_1
			amts_png_file_2
			amts_png_file_3
			amts_data_file_1
			amts_data_file_2
			amts_data_file_3
			amts_png_file_current_page
			amts_data_file_utf8
			amts_png_file_utf8
		the last of which contains the LaTeX command \\thepage (such that
		LaTeX can use this in, say, page headers) but omitting the .png
		(for which LaTeX will look by itself),
		note that you will have to use the 2nd- or 3rd-pass placeholder
		format if you plan to insert the above because they will only be
		available by first (or second) pass processing of the initial
		placeholder "current_meds_AMTS"
	""",
	'current_meds_AMTS_enhanced': """emit LaTeX longtable lines with appropriate page breaks:
		this returns the same content as current_meds_AMTS except that
		it does not truncate output data whenever possible
	""",

	'current_meds_table': "emits a LaTeX table, no arguments",
	'current_meds_notes': "emits a LaTeX table, no arguments",
	'lab_table': "emits a LaTeX table, no arguments",
	'test_results': "args: <%(field)s-template>//<date format>//<line separator (EOL)>",
	'most_recent_test_results': """most recent test results formatted as defined in <template>:
		args: <dfmt=...>//<tmpl=...>//<sep=...>
		<dfmt=...>: strftime format string for test result timestamps,
		<tmpl=...>: target format specific %s-template, applied to each test result
		<sep=...>: line separator, can be a Python string escape, such as \n
	""",
	'latest_vaccs_table': "emits a LaTeX table, no arguments",
	'vaccination_history': "args: <%(field)s-template//date format> to format one vaccination per line",
	'allergy_state': "no arguments",
	'allergies': "args: line template, one allergy per line",
	'allergy_list': "args holds: template per allergy, all allergies on one line",
	'problems': "args holds: line template, one problem per line",
	'diagnoses': 'args: line template, one diagnosis per line',
	'PHX': "Past medical HiXtory; args: line template//separator//strftime date format",
	'encounter_list': "args: per-encounter template, each ends up on one line",

	'documents': """retrieves documents from the archive:
		args:	<select>//<description>//<template>//<path template>//<path>
		select:	let user select which documents to include, optional, if not given: all documents included
		description:	whether to include descriptions, optional
		template:	something %(field)s something else (do not include '//' or '::' itself in the template)
		path template:	the template for outputting the path to exported
			copies of the document pages, if not given no pages are exported,
			this template can contain "%(name)s" and/or "%(fullpath)s" which 
			is replaced by the appropriate value for each exported file
		path:	into which path to export copies of the document pages, temp dir if not given""",

	'reminders': """patient reminders:
		args:	<template>//<date format>
		template:	something %(field)s something else (do not include '//' or '::' itself in the template)""",

	'external_care': """External care entries:
		args:	<template>
		template:	something %(field)s something else (do not include '//' or '::' itself in the template)""",

	# provider related:
	'current_provider': "no arguments",
	'current_provider_name': """formatted name of current provider:
		args: <template>,
		template:	something %(field)s something else (do not include '//' or '::' itself in the template)
	""",
	'current_provider_title': """formatted name of current provider:
		args: <optional template>,
		template:	something %(title)s something else (do not include '//' or '::' itself in the template)
	""",
	'current_provider_firstnames': """formatted name of current provider:
		args: <optional template>,
		template:	something %(firstnames)s something else (do not include '//' or '::' itself in the template)
	""",
	'current_provider_lastnames': """formatted name of current provider:
		args: <optional template>,
		template:	something %(lastnames)s something else (do not include '//' or '::' itself in the template)
	""",
	'current_provider_external_id': "args: <type of ID>//<issuer of ID>",
	'primary_praxis_provider': "primary provider for current patient in this praxis",
	'primary_praxis_provider_external_id': "args: <type of ID>//<issuer of ID>",


	# praxis related:
	'praxis': """retrieve current branch of your praxis:
		args: <template>//select
		template:		something %(field)s something else (do not include '//' or '::' itself in the template)
		select:			if this is present allow selection of the branch rather than using the current branch""",

	'praxis_address': "args: <optional formatting template>",
	'praxis_comm': "args: type//<optional formatting template>",
	'praxis_id': "args: <type of ID>//<issuer of ID>//<optional formatting template>",
	'praxis_vcf': """returns path to VCF for current praxis branch
		args: <template>
		template: %s-template for path
	""",
	u'praxis_mcf': u"""returns MECARD for current praxis branch
		args: <format>//<template>
		format: fmt=qr|mcf|txt
			qr: QR code png file path,
			mcf: MECARD .mcf file path,
			txt: MECARD string,
			default - if omitted - is "txt",
		template: tmpl=<%s-template string>, "%s" if omitted
	""",
	u'praxis_scan2pay': u"""return scan2pay data or QR code for current praxis
		args: <format>,
			format: fmt=qr|txt
				qr: QR code png file path,
				txt: scan2pay data string,
				default - if omitted: qr
	""",

	# billing related:
	'bill': """retrieve a bill
		args: <template>//<date format>
		template:		something %(field)s something else (do not include '//' or '::' itself in the template)
		date format:	strftime date format""",
	'bill_scan2pay': u"""return scan2pay data or QR code for a bill
		args: <format>,
			format: fmt=qr|txt
				qr: QR code png file path,
				txt: scan2pay data string,
				default - if omitted: qr
	""",
	'bill_item': """retrieve the items of a previously retrieved (and therefore cached until the next retrieval) bill
		args: <template>//<date format>
		template:		something %(field)s something else (do not include '//' or '::' itself in the template)
		date format:	strftime date format""",
	'bill_adr_street': "args: optional template (%s-style formatting template); cached per bill",
	'bill_adr_number': "args: optional template (%s-style formatting template); cached per bill",
	'bill_adr_subunit': "args: optional template (%s-style formatting template); cached per bill",
	'bill_adr_location': "args: optional template (%s-style formatting template); cached per bill",
	'bill_adr_suburb': "args: optional template (%s-style formatting template); cached per bill",
	'bill_adr_postcode': "args: optional template (%s-style formatting template); cached per bill",
	'bill_adr_region': "args: optional template (%s-style formatting template); cached per bill",
	'bill_adr_country': "args: optional template (%s-style formatting template); cached per bill"

}

known_variant_placeholders = list(__known_variant_placeholders)


# https://help.libreoffice.org/Common/List_of_Regular_Expressions
# except that OOo cannot be non-greedy |-(
#default_placeholder_regex = r'\$<.+?>\$'				# previous working placeholder
	# regex logic:
	# starts with "$"
	# followed by "<"
	# followed by > 0 characters but NOT "<" but ONLY up to the NEXT ":"
	# followed by "::"
	# followed by any number of characters  but ONLY up to the NEXT ":"
	# followed by "::"
	# followed by any number of numbers
	# followed by ">"
	# followed by "$"

# previous:
default_placeholder_regex = r'\$<[^<:]+::.*?::\d*?>\$|\$<[^<:]+::.*?::\d+-\d+>\$'         # this one works [except that OOo cannot be non-greedy |-(    ]
first_pass_placeholder_regex = r'|'.join ([
	r'\$<[^<:]+::.*?(?=::\d*?>\$)::\d*?>\$',
	r'\$<[^<:]+::.*?(?=::\d+-\d+>\$)::\d+-\d+>\$'
])
second_pass_placeholder_regex = r'|'.join ([
	r'\$<<[^<:]+?::.*?(?=::\d*?>>\$)::\d*?>>\$',
	r'\$<<[^<:]+?::.*?(?=::\d+-\d+>>\$)::\d+-\d+>>\$'
])
third_pass_placeholder_regex = r'|'.join ([
	r'\$<<<[^<:]+?::.*?(?=::\d*?>>>\$)::\d*?>>>\$',
	r'\$<<<[^<:]+?::.*?(?=::\d+-\d+>>>\$)::\d+-\d+>>>\$'
])

default_placeholder_start = '$<'
default_placeholder_end = '>$'

#=====================================================================
def show_placeholders():

	fname = gmTools.get_unique_filename(prefix = 'gm-placeholders-', suffix = '.txt')
	ph_file = open(fname, mode = 'wt', encoding = 'utf8', errors = 'replace')

	ph_file.write('Here you can find some more documentation on placeholder use:\n')
	ph_file.write('\n https://www.gnumed.de/bin/view/Gnumed/GmManualLettersForms\n\n\n')

	ph_file.write('Variable placeholders:\n')
	ph_file.write('Usage: $<PLACEHOLDER_NAME::ARGUMENTS::REGION_DEFINITION>$)\n')
	ph_file.write(' REGION_DEFINITION:\n')
	ph_file.write('* a single number specifying the maximum output length or\n')
	ph_file.write('* a number, a "-", followed by a second number specifying the region of the string to return\n')
	ph_file.write('ARGUMENTS:\n')
	ph_file.write('* depend on the actual placeholder (see there)\n')
	ph_file.write('* if a template is supported it will be used to %-format the output\n')
	ph_file.write('* templates may be either %s-style or %(name)s-style\n')
	ph_file.write('* templates cannot contain "::"\n')
	ph_file.write('* templates cannot contain whatever the arguments divider is set to (default "//")\n')
	for ph in known_variant_placeholders:
		txt = __known_variant_placeholders[ph]
		ph_file.write('\n')
		ph_file.write('	---=== %s ===---\n' % ph)
		ph_file.write('\n')
		ph_file.write(txt)
		ph_file.write('\n\n')
	ph_file.write('\n')

	ph_file.write('Known injectable placeholders (use like: $<PLACEHOLDER_NAME::ARGUMENTS::MAX OUTPUT LENGTH>$):\n')
	for ph in known_injectable_placeholders:
		ph_file.write(' %s\n' % ph)
	ph_file.write('\n')

	ph_file.close()
	gmMimeLib.call_viewer_on_file(aFile = fname, block = False)

#=====================================================================
class gmPlaceholderHandler(gmBorg.cBorg):
	"""Returns values for placeholders.

	- patient related placeholders operate on the currently active patient
	- is passed to the forms handling code, for example

	Return values when .debug is False:
	- errors with placeholders return None
	- placeholders failing to resolve to a value return an empty string

	Return values when .debug is True:
	- errors with placeholders return an error string
	- placeholders failing to resolve to a value return a warning string

	There are several types of placeholders:

	injectable placeholders
		- they must be set up before use by set_placeholder()
		- they should be removed after use by unset_placeholder()
		- the syntax is like extended static placeholders
		- known ones are listed in known_injectable_placeholders
		- per-form ones can be used but must exist before
		  the form is processed

	variant placeholders
		- those are listed in known_variant_placeholders
		- they are parsed into placeholder, data, and maximum length
		- the length is optional
		- data is passed to the handler

	Note that this cannot be called from a non-gui thread unless
	wrapped in wx.CallAfter().
	"""
	def __init__(self, *args, **kwargs):

		self.pat = gmPerson.gmCurrentPatient()
		self.debug:bool = False

		self.invalid_placeholder_template:str = _('invalid placeholder >>>>>%s<<<<<')

		self.__injected_placeholders:dict = {}
		self.__cache:dict = {}

		self.__esc_style:str = None
		self.__esc_func = lambda x:x

		self.__ellipsis:str = None
		self.__args_divider:str = '//'
		self.__data_encoding:str = None
		self.__data_encoding_strict:bool = False

	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def set_placeholder(self, key=None, value=None, known_only=True):
		_log.debug('setting [%s]', key)
		if key not in known_injectable_placeholders:
			if known_only:
				raise ValueError('un-injectable placeholder [%s]' % key)

			_log.debug('placeholder [%s] not known as injectable', key)

		self.__injected_placeholders[key] = value

	#--------------------------------------------------------
	def unset_placeholder(self, key=None):
		_log.debug('unsetting [%s]', key)
		try:
			del self.__injected_placeholders[key]
		except KeyError:
			_log.debug('injectable placeholder [%s] unknown', key)

	#--------------------------------------------------------
	def set_cache_value(self, key=None, value=None):
		self.__cache[key] = value
	#--------------------------------------------------------
	def unset_cache_value(self, key=None):
		del self.__cache[key]

	#--------------------------------------------------------
	def _set_escape_style(self, escape_style=None):
		self.__esc_style = escape_style
		return

	escape_style = property(lambda x:x, _set_escape_style)

	#--------------------------------------------------------
	def _get_escape_function(self):
		return self.__esc_func

	def _set_escape_function(self, escape_function=None):
		if escape_function is None:
			self.__esc_func = lambda x:x
			return
		if not callable(escape_function):
			raise ValueError('[%s._set_escape_function]: <%s> not callable' % (self.__class__.__name__, escape_function))
		self.__esc_func = escape_function
		return

	escape_function = property(_get_escape_function, _set_escape_function)

	#--------------------------------------------------------
	def _get_ellipsis(self):
		return self.__ellipsis

	def _set_ellipsis(self, ellipsis):
		if ellipsis == 'NONE':
			ellipsis = None
		self.__ellipsis = ellipsis

	ellipsis = property(_get_ellipsis, _set_ellipsis)

	#--------------------------------------------------------
	def _get_arguments_divider(self):
		return self.__args_divider

	def _set_arguments_divider(self, divider):
		if divider == 'DEFAULT':
			divider = '//'
		self.__args_divider = divider

	arguments_divider = property(_get_arguments_divider, _set_arguments_divider)

	#--------------------------------------------------------
	def _get_data_encoding(self) -> str:
		return self.__data_encoding

	def _set_data_encoding(self, encoding:str):
		if encoding == 'NONE':
			self.__data_encoding = None
			self.__data_encoding_strict = False

		self.__data_encoding_strict = False
		if encoding.endswith('-strict'):
			self.__data_encoding_strict = True
			encoding = encoding[:-7]
		try:
			codecs.lookup(encoding)
			self.__data_encoding = encoding
		except LookupError:
			_log.error('<codecs> module can NOT handle encoding [%s]' % encoding)

	data_encoding = property(_get_data_encoding, _set_data_encoding)

	#--------------------------------------------------------
	placeholder_regex = property(lambda x: default_placeholder_regex)

	first_pass_placeholder_regex = property(lambda x: first_pass_placeholder_regex)
	second_pass_placeholder_regex = property(lambda x: second_pass_placeholder_regex)
	third_pass_placeholder_regex = property(lambda x: third_pass_placeholder_regex)

	#--------------------------------------------------------
	def __parse_region_definition(self, region_str):
		region_str = region_str.strip()

		if region_str == '':
			return None, None

		try:
			pos_last_char = int(region_str)
			return 0, pos_last_char
		except (TypeError, ValueError):
			_log.debug('region definition not a simple length')

		# note that we only check for "legality", not for reasonable bounds
		first_last = region_str.split('-')
		if len(first_last) != 2:
			_log.error('invalid placeholder region definition: %s', region_str)
			raise ValueError

		try:
			pos_first_char = int(first_last[0].strip())
			pos_last_char = int(first_last[1].strip())
		except (TypeError, ValueError):
			_log.error('invalid placeholder region definition: %s', region_str)
			raise ValueError

		# user says 1,2,... (= character position in string), Python needs 0,1,... (indexes 0-based)
		if pos_first_char > 0:
			pos_first_char -= 1

		return pos_first_char, pos_last_char

	#--------------------------------------------------------
	def __make_compatible_with_encoding(self, data_str):
		if self.__data_encoding is None:
			return data_str

		try:
			codecs.encode(data_str, self.__data_encoding, 'strict')
			return data_str
		except UnicodeEncodeError:
			_log.error('cannot strict-encode string into [%s]: %s', self.__data_encoding, data_str)

		if self.__data_encoding_strict:
			return 'not compatible with encoding [%s]: %s' % (self.__data_encoding, data_str)

		try:
			import unidecode
		except ImportError:
			_log.debug('cannot transliterate, <unidecode> module not installed')
			return codecs.encode(data_str, self.__data_encoding, 'replace').decode(self.__data_encoding)

		return unidecode.unidecode(data_str).decode('utf8')

	#--------------------------------------------------------
	# __getitem__ API
	#--------------------------------------------------------
	def __getitem__(self, placeholder):
		"""Map self['placeholder'] to self.placeholder.

		This is useful for replacing placeholders parsed out
		of documents as strings.

		Unknown/invalid placeholders still deliver a result but
		it will be glaringly obvious if debugging is enabled.
		"""
		_log.debug('replacing [%s]', placeholder)

		original_placeholder_def = placeholder

		# remove leading/trailing '$<(<<)' and '(>>)>$'
		if placeholder.startswith(default_placeholder_start):
			placeholder = placeholder.lstrip('$').lstrip('<')
			if placeholder.endswith(default_placeholder_end):
				placeholder = placeholder.rstrip('$').rstrip('>')
			else:
				_log.error('placeholder must either start with [%s] and end with [%s] or neither of both', default_placeholder_start, default_placeholder_end)
				if self.debug:
					return self._escape(self.invalid_placeholder_template % original_placeholder_def)
				return None

		# injectable placeholder ?
		parts = placeholder.split('::::', 1)
		if len(parts) == 2:
			ph_name, region_str = parts
			is_an_injectable = True
			try:
				val = self.__injected_placeholders[ph_name]
			except KeyError:
				is_an_injectable = False
			except Exception:
				_log.exception('injectable placeholder handling error: %s', original_placeholder_def)
				if self.debug:
					return self._escape(self.invalid_placeholder_template % original_placeholder_def)

				return None

			if is_an_injectable:
				if val is None:
					if self.debug:
						return self._escape('injectable placeholder [%s]: no value available' % ph_name)
					return placeholder
				try:
					pos_first_char, pos_last_char = self.__parse_region_definition(region_str)
				except ValueError:
					if self.debug:
						return self._escape(self.invalid_placeholder_template % original_placeholder_def)
					return None
				if pos_last_char is None:
					return self.__make_compatible_with_encoding(val)
				# ellipsis needed ?
				if len(val) > (pos_last_char - pos_first_char):
					# ellipsis wanted ?
					if self.__ellipsis is not None:
						return self.__make_compatible_with_encoding(val[pos_first_char:(pos_last_char-len(self.__ellipsis))] + self.__ellipsis)
				return self.__make_compatible_with_encoding(val[pos_first_char:pos_last_char])

		# variable placeholders
		if len(placeholder.split('::', 2)) < 3:
			_log.error('invalid placeholder structure: %s', original_placeholder_def)
			if self.debug:
				return self._escape(self.invalid_placeholder_template % original_placeholder_def)
			return None

		ph_name, data_and_lng = placeholder.split('::', 1)		# note: split _is_ lsplit
		options, region_str = data_and_lng.rsplit('::', 1)
		_log.debug('placeholder parts: name=[%s]; region_def=[%s]; options=>>>%s<<<', ph_name, region_str, options)
		try:
			pos_first_char, pos_last_char = self.__parse_region_definition(region_str)
		except ValueError:
			if self.debug:
				return self._escape(self.invalid_placeholder_template % original_placeholder_def)
			return None

		handler = getattr(self, '_get_variant_%s' % ph_name, None)
		if handler is None:
			_log.warning('no handler <_get_variant_%s> for placeholder %s', ph_name, original_placeholder_def)
			if self.debug:
				return self._escape(self.invalid_placeholder_template % original_placeholder_def)
			return None

		try:
			val = handler(data = options)
			if pos_last_char is None:
				return self.__make_compatible_with_encoding(val)
			# ellipsis needed ?
			if len(val) > (pos_last_char - pos_first_char):
				# ellipsis wanted ?
				if self.__ellipsis is not None:
					return self.__make_compatible_with_encoding(val[pos_first_char:(pos_last_char-len(self.__ellipsis))] + self.__ellipsis)
			return self.__make_compatible_with_encoding(val[pos_first_char:pos_last_char])

		except Exception:
			_log.exception('placeholder handling error: %s', original_placeholder_def)
			if self.debug:
				return self._escape(self.invalid_placeholder_template % original_placeholder_def)
			return None

		_log.error('something went wrong, should never get here')
		return None

	#--------------------------------------------------------
	# placeholder handlers
	#--------------------------------------------------------
	def _get_variant_ph_cfg(self, data=None):
		options = data.split('//')		# ALWAYS use '//' for splitting, regardless of self.__args_divider
		name = options[0]
		val = options[1]
		if name == 'ellipsis':
			self.ellipsis = val
		elif name == 'argumentsdivider':
			self.arguments_divider = val
		elif name == 'encoding':
			self.data_encoding = val
		if len(options) > 2:
			return options[2] % {'name': name, 'value': val}
		return ''
	#--------------------------------------------------------
	def _get_variant_client_version(self, data=None):
		return self._escape (
			gmTools.coalesce (
				_cfg.get(option = 'client_version'),
				'%s' % self.__class__.__name__
			)
		)
	#--------------------------------------------------------
	def _get_variant_reminders(self, data=None):

		from Gnumed.wxpython import gmProviderInboxWidgets

		template = _('due %(due_date)s: %(comment)s (%(interval_due)s)')
		date_format = '%Y %b %d'

		data_parts = data.split(self.__args_divider)

		if len(data_parts) > 0:
			if data_parts[0].strip() != '':
				template = data_parts[0]

		if len(data_parts) > 1:
			if data_parts[1].strip() != '':
				date_format = data_parts[1]

		reminders = gmProviderInboxWidgets.manage_reminders(patient = self.pat.ID)

		if reminders is None:
			return ''

		if len(reminders) == 0:
			return ''

		lines = [ template % r.fields_as_dict(date_format = date_format, escape_style = self.__esc_style) for r in reminders ]

		return '\n'.join(lines)
	#--------------------------------------------------------
	def _get_variant_external_care(self, data=None):

		from Gnumed.wxpython import gmExternalCareWidgets
		external_cares = gmExternalCareWidgets.manage_external_care()

		if external_cares is None:
			return ''

		if len(external_cares) == 0:
			return ''

		template = data
		lines = [ template % ext.fields_as_dict(escape_style = self.__esc_style) for ext in external_cares ]

		return '\n'.join(lines)
	#--------------------------------------------------------
	def _get_variant_documents(self, data=None):

		select = False
		include_descriptions = False
		template = '%s'
		path_template = None
		export_path = None

		data_parts = data.split(self.__args_divider)

		if 'select' in data_parts:
			select = True
			data_parts.remove('select')

		if 'description' in data_parts:
			include_descriptions = True
			data_parts.remove('description')

		template = data_parts[0]

		if len(data_parts) > 1:
			path_template = data_parts[1]

		if len(data_parts) > 2:
			export_path = data_parts[2]

		# create path
		if export_path is not None:
			export_path = os.path.normcase(os.path.expanduser(export_path))
			gmTools.mkdir(export_path)

		# select docs
		if select:
			docs = gmDocumentWidgets.manage_documents(msg = _('Select the patient documents to reference from the new document.'), single_selection = False)
		else:
			docs = self.pat.document_folder.documents

		if docs is None:
			return ''

		lines = []
		for doc in docs:
			lines.append(template % doc.fields_as_dict(date_format = '%Y %b %d', escape_style = self.__esc_style))
			if include_descriptions:
				for desc in doc.get_descriptions(max_lng = None):
					lines.append(self._escape(desc['text'] + '\n'))
			if path_template is not None:
				for part_name in doc.save_parts_to_files(export_dir = export_path):
					path, name = os.path.split(part_name)
					lines.append(path_template % {'fullpath': part_name, 'name': name})

		return '\n'.join(lines)
	#--------------------------------------------------------
	def _get_variant_encounter_list(self, data=None):

		encounters = gmEncounterWidgets.select_encounters(single_selection = False)
		if not encounters:
			return ''

		template = data

		lines = []
		for enc in encounters:
			try:
				lines.append(template % enc.fields_as_dict(date_format = '%Y %b %d', escape_style = self.__esc_style))
			except Exception:
				lines.append('error formatting encounter')
				_log.exception('problem formatting encounter list')
				_log.error('template: %s', template)
				_log.error('encounter: %s', enc)

		return '\n'.join(lines)
	#--------------------------------------------------------
	def _get_variant_soap_for_encounters(self, data=None):
		"""Select encounters from list and format SOAP thereof.

		data: soap_cats (' ' -> None -> admin) // date format
		"""
		# defaults
		cats = None
		date_format = None

		if data is not None:
			data_parts = data.split(self.__args_divider)

			# part[0]: categories
			if len(data_parts[0]) > 0:
				cats = []
				if ' ' in data_parts[0]:
					cats.append(None)
					data_parts[0] = data_parts[0].replace(' ', '')
				cats.extend(list(data_parts[0]))

			# part[1]: date format
			if len(data_parts) > 1:
				if len(data_parts[1]) > 0:
					date_format = data_parts[1]

		encounters = gmEncounterWidgets.select_encounters(single_selection = False)
		if not encounters:
			return ''

		chunks = []
		for enc in encounters:
			chunks.append(enc.format_latex (
				date_format = date_format,
				soap_cats = cats,
				soap_order = 'soap_rank, date'
			))

		return ''.join(chunks)

	#--------------------------------------------------------
	def _get_variant_emr_journal(self, data=None):
		# default: all categories, neutral template
		cats = list('soapu')
		cats.append(None)
		template = '%s'
		line_length = 9999
		time_range = None

		if data is not None:
			data_parts = data.split(self.__args_divider)

			# part[0]: categories
			cats = []
			# ' ' -> None == admin
			for c in list(data_parts[0]):
				if c == ' ':
					c = None
				cats.append(c)
			# '' -> SOAP + None
			if cats == '':
				cats = list('soapu').append(None)

			# part[1]: template
			if len(data_parts) > 1:
				template = data_parts[1]

			# part[2]: line length
			if len(data_parts) > 2:
				try:
					line_length = int(data_parts[2])
				except Exception:
					line_length = 9999

			# part[3]: weeks going back in time
			if len(data_parts) > 3:
				try:
					time_range = 7 * int(data_parts[3])
				except Exception:
					#time_range = None			# infinite
					# pass on literally, meaning it must be a valid PG interval string
					time_range = data_parts[3]

		emr_as_journal = self.pat.emr.get_as_journal(soap_cats = cats, time_range = time_range)
		if len(emr_as_journal) == 0:
			return ''

		lines = []
		for journal_line in emr_as_journal:
			line_dict = self._escape_dict_like(dict_like = journal_line)	#, date_format='%Y %b %d  %H:%M', none_string = '', bool_strings = None
			try:
				lines.append((template % line_dict)[:line_length])
			except KeyError:
				return 'invalid key in template [%s], valid keys: %s]' % (template, emr_as_journal[0].keys())
		return '\n'.join(lines)

	#--------------------------------------------------------
	def _get_variant_soap_by_issue(self, data=None):
		return self.__get_variant_soap_by_issue_or_episode(data = data, mode = 'issue')

	#--------------------------------------------------------
	def _get_variant_soap_by_episode(self, data=None):
		return self.__get_variant_soap_by_issue_or_episode(data = data, mode = 'episode')

	#--------------------------------------------------------
	def __get_variant_soap_by_issue_or_episode(self, data=None, mode=None):

		# default: all categories, neutral template
		cats = list('soapu')
		cats.append(None)

		date_format = None
		template = '%s'

		if data is not None:
			data_parts = data.split(self.__args_divider)

			# part[0]: categories
			if len(data_parts[0]) > 0:
				cats = []
				if ' ' in data_parts[0]:
					cats.append(None)
				cats.extend(list(data_parts[0].replace(' ', '')))

			# part[1]: date format
			if len(data_parts) > 1:
				if len(data_parts[1]) > 0:
					date_format = data_parts[1]

			# part[2]: template
			if len(data_parts) > 2:
				if len(data_parts[2]) > 0:
					template = data_parts[2]

		if mode == 'issue':
			narr = gmNarrativeWorkflows.select_narrative_by_issue(soap_cats = cats)
		else:
			narr = gmNarrativeWorkflows.select_narrative_by_episode(soap_cats = cats)

		if narr is None:
			return ''

		if len(narr) == 0:
			return ''

		try:
			narr = [ template % n.fields_as_dict(date_format = date_format, escape_style = self.__esc_style) for n in narr ]
		except KeyError:
			return 'invalid key in template [%s], valid keys: %s]' % (template, narr[0].keys())

		return '\n'.join(narr)
	#--------------------------------------------------------
	def _get_variant_progress_notes(self, data=None):
		return self._get_variant_soap(data = data)
	#--------------------------------------------------------
	def _get_variant_soap_s(self, data=None):
		return self._get_variant_soap(data = 's')
	#--------------------------------------------------------
	def _get_variant_soap_o(self, data=None):
		return self._get_variant_soap(data = 'o')
	#--------------------------------------------------------
	def _get_variant_soap_a(self, data=None):
		return self._get_variant_soap(data = 'a')
	#--------------------------------------------------------
	def _get_variant_soap_p(self, data=None):
		return self._get_variant_soap(data = 'p')
	#--------------------------------------------------------
	def _get_variant_soap_u(self, data=None):
		return self._get_variant_soap(data = 'u')
	#--------------------------------------------------------
	def _get_variant_soap_admin(self, data=None):
		return self._get_variant_soap(data = ' ')
	#--------------------------------------------------------
	def _get_variant_soap(self, data=None):

		# default: all categories, neutral template
		cats = list('soapu')
		cats.append(None)
		template = '%(narrative)s'

		if data is not None:
			data_parts = data.split(self.__args_divider)

			# part[0]: categories
			cats = []
			# ' ' -> None == admin
			for cat in list(data_parts[0]):
				if cat == ' ':
					cat = None
				cats.append(cat)
			# '' -> SOAP + None
			if cats == '':
				cats = list('soapu')
				cats.append(None)

			# part[1]: template
			if len(data_parts) > 1:
				template = data_parts[1]

		#narr = gmNarrativeWorkflows.select_narrative_from_episodes(soap_cats = cats)
		narr = gmNarrativeWorkflows.select_narrative(soap_cats = cats)

		if narr is None:
			return ''

		if len(narr) == 0:
			return ''

		# if any "%s" is in the template there cannot be any %(field)s
		# and we also restrict the fields to .narrative (this is the
		# old placeholder behaviour
		if '%s' in template:
			narr = [ self._escape(n['narrative']) for n in narr ]
		else:
			narr = [ n.fields_as_dict(escape_style = self.__esc_style) for n in narr ]

		try:
			narr = [ template % n for n in narr ]
		except KeyError:
			return 'invalid key in template [%s], valid keys: %s]' % (template, narr[0].keys())
		except TypeError:
			return 'cannot mix "%%s" and "%%(field)s" in template [%s]' % template

		return '\n'.join(narr)

	#--------------------------------------------------------
	def _get_variant_title(self, data=None):
		return self._get_variant_name(data = '%(title)s')
	#--------------------------------------------------------
	def _get_variant_firstname(self, data=None):
		return self._get_variant_name(data = '%(firstnames)s')
	#--------------------------------------------------------
	def _get_variant_lastname(self, data=None):
		return self._get_variant_name(data = '%(lastnames)s')
	#--------------------------------------------------------
	def _get_variant_name(self, data=None):
		if not data:
			data = '%(title)s %(firstnames)s %(lastnames)s'
		name = self.pat.get_active_name()
		parts = {
			'title': self._escape(gmTools.coalesce(name['title'], '')),
			'firstnames': self._escape(name['firstnames']),
			'lastnames': self._escape(name['lastnames']),
			'preferred': self._escape(gmTools.coalesce (
				value2test = name['preferred'],
				return_instead = ' ',
				template4value = ' "%s" '
			))
		}
		return data % parts

	#--------------------------------------------------------
	def _get_variant_date_of_birth(self, data=None):
		if not data:
			data = '%Y %b %d'
		return self.pat.get_formatted_dob(format = data)

	#--------------------------------------------------------
	# FIXME: extend to all supported genders
	def _get_variant_gender_mapper(self, data='male//female//other'):

		values = data.split('//', 2)

		if len(values) == 2:
			male_value, female_value = values
			other_value = '<unknown gender>'
		elif len(values) == 3:
			male_value, female_value, other_value = values
		else:
			return _('invalid gender mapping layout: [%s]') % data

		if self.pat['gender'] == 'm':
			return self._escape(male_value)

		if self.pat['gender'] == 'f':
			return self._escape(female_value)

		return self._escape(other_value)
	#--------------------------------------------------------
	# address related placeholders
	#--------------------------------------------------------
	def __get_variant_gen_adr_part(self, data='?', part=None):

		template = '%s'
		msg = _('Select the address you want to use !')
		cache_id = ''
		options = data.split('//', 4)
		if len(options) > 0:
			template = options[0]
			if template.strip() == '':
				template = '%s'
		if len(options) > 1:
			msg = options[1]
		if len(options) > 2:
			cache_id = options[2]

		cache_key = 'generic_address::' + cache_id
		try:
			adr2use = self.__cache[cache_key]
			_log.debug('cache hit (%s): [%s]', cache_key, adr2use)
		except KeyError:
			adr2use = None

		if adr2use is None:
			dlg = gmAddressWidgets.cAddressSelectionDlg(None, -1)
			dlg.message = msg
			choice = dlg.ShowModal()
			adr2use = dlg.address
			dlg.DestroyLater()
			if choice == wx.ID_CANCEL:
				return ''
			self.__cache[cache_key] = adr2use

		return template % self._escape(adr2use[part])
	#--------------------------------------------------------
	def _get_variant_gen_adr_street(self, data='?'):
		return self.__get_variant_gen_adr_part(data = data, part = 'street')
	#--------------------------------------------------------
	def _get_variant_gen_adr_number(self, data='?'):
		return self.__get_variant_gen_adr_part(data = data, part = 'number')
	#--------------------------------------------------------
	def _get_variant_gen_adr_subunit(self, data='?'):
		return self.__get_variant_gen_adr_part(data = data, part = 'subunit')
	#--------------------------------------------------------
	def _get_variant_gen_adr_location(self, data='?'):
		return self.__get_variant_gen_adr_part(data = data, part = 'urb')
	#--------------------------------------------------------
	def _get_variant_gen_adr_suburb(self, data='?'):
		return self.__get_variant_gen_adr_part(data = data, part = 'suburb')
	#--------------------------------------------------------
	def _get_variant_gen_adr_postcode(self, data='?'):
		return self.__get_variant_gen_adr_part(data = data, part = 'postcode')
	#--------------------------------------------------------
	def _get_variant_gen_adr_region(self, data='?'):
		return self.__get_variant_gen_adr_part(data = data, part = 'l10n_region')
	#--------------------------------------------------------
	def _get_variant_gen_adr_country(self, data='?'):
		return self.__get_variant_gen_adr_part(data = data, part = 'l10n_country')
	#--------------------------------------------------------
	def __get_variant_receiver_part(self, data='%s', part=None):

		template = '%s'
		cache_id = ''
		options = data.split('//', 3)
		if len(options) > 0:
			template = options[0]
			if template.strip() == '':
				template = '%s'
		if len(options) > 1:
			cache_id = options[1]

		cache_key = 'receiver::' + cache_id
		try:
			name, adr = self.__cache[cache_key]
			_log.debug('cache hit (%s): [%s:%s]', cache_key, name, adr)
		except KeyError:
			name = None
			adr = None

		if name is None:
			from Gnumed.wxpython import gmFormWidgets
			dlg = gmFormWidgets.cReceiverSelectionDlg(None, -1)
			dlg.patient = self.pat
			choice = dlg.ShowModal()
			name = dlg.name
			adr = dlg.address
			dlg.DestroyLater()
			if choice == wx.ID_CANCEL:
				return ''
			self.__cache[cache_key] = (name, adr)

		if part == 'name':
			return template % self._escape(name)

		return template % self._escape(gmTools.coalesce(adr[part], ''))
	#--------------------------------------------------------
	def _get_variant_receiver_name(self, data='%s'):
		return self.__get_variant_receiver_part(data = data, part = 'name')
	#--------------------------------------------------------
	def _get_variant_receiver_street(self, data='%s'):
		return self.__get_variant_receiver_part(data = data, part = 'street')
	#--------------------------------------------------------
	def _get_variant_receiver_number(self, data='%s'):
		return self.__get_variant_receiver_part(data = data, part = 'number')
	#--------------------------------------------------------
	def _get_variant_receiver_subunit(self, data='%s'):
		return self.__get_variant_receiver_part(data = data, part = 'subunit')
	#--------------------------------------------------------
	def _get_variant_receiver_location(self, data='%s'):
		return self.__get_variant_receiver_part(data = data, part = 'urb')
	#--------------------------------------------------------
	def _get_variant_receiver_suburb(self, data='%s'):
		return self.__get_variant_receiver_part(data = data, part = 'suburb')
	#--------------------------------------------------------
	def _get_variant_receiver_postcode(self, data='%s'):
		return self.__get_variant_receiver_part(data = data, part = 'postcode')
	#--------------------------------------------------------
	def _get_variant_receiver_region(self, data='%s'):
		return self.__get_variant_receiver_part(data = data, part = 'l10n_region')
	#--------------------------------------------------------
	def _get_variant_receiver_country(self, data='%s'):
		return self.__get_variant_receiver_part(data = data, part = 'l10n_country')

	#--------------------------------------------------------
	def _get_variant_patient_address(self, data=''):
		kwds = {'fmt': 'not_defined'}
		pos = {
			'type': '',
			'tmpl': _('%(street)s %(number)s, %(postcode)s %(urb)s, %(l10n_region)s, %(l10n_country)s')
		}

		opts = self._parse_ph_options (
			options_data = data,
			kwd_defaults = kwds,
			pos_defaults = pos
		)
		adr_type = opts['type']
		orig_type = adr_type
		if adr_type != '':
			adrs = self.pat.get_addresses(address_type = adr_type)
			if len(adrs) == 0:
				_log.warning('no address for type [%s]', adr_type)
				adr_type = ''
		if adr_type == '':
			_log.debug('asking user for address type')
			adr = gmPersonContactWidgets.select_address(missing = orig_type, person = self.pat)
			if adr is None:
				if self.debug:
					return _('no address type replacement selected')
				return ''

			adr_type = adr['address_type']

		adr = self.pat.get_addresses(address_type = adr_type)[0]
		if opts['fmt'] == 'mapurl':
			return adr.as_map_url

		try:
			return opts['tmpl'] % adr.fields_as_dict(escape_style = self.__esc_style)

		except Exception:
			_log.exception('error formatting address')
			_log.error('template: %s', opts['tmpl'])
		return None

	#--------------------------------------------------------
	def __get_variant_adr_part(self, data='?', part=None):
		requested_type = data.strip()
		cache_key = 'adr-type-%s' % requested_type
		try:
			type2use = self.__cache[cache_key]
			_log.debug('cache hit (%s): [%s] -> [%s]', cache_key, requested_type, type2use)
		except KeyError:
			type2use = requested_type
			if type2use != '':
				adrs = self.pat.get_addresses(address_type = type2use)
				if len(adrs) == 0:
					_log.warning('no address of type [%s] for <%s> field extraction', requested_type, part)
					type2use = ''
			if type2use == '':
				_log.debug('asking user for replacement address type')
				adr = gmPersonContactWidgets.select_address(missing = requested_type, person = self.pat)
				if adr is None:
					_log.debug('no replacement selected')
					if self.debug:
						return self._escape(_('no address type replacement selected'))
					return ''
				type2use = adr['address_type']
				self.__cache[cache_key] = type2use
				_log.debug('caching (%s): [%s] -> [%s]', cache_key, requested_type, type2use)

		part_data = self.pat.get_addresses(address_type = type2use)[0][part]
		if part_data is None:
			part_data = ''	# do escape empty string since we never know what target formats need
		return self._escape(part_data)

	#--------------------------------------------------------
	def _get_variant_adr_street(self, data='?'):
		return self.__get_variant_adr_part(data = data, part = 'street')
	#--------------------------------------------------------
	def _get_variant_adr_number(self, data='?'):
		return self.__get_variant_adr_part(data = data, part = 'number')
	#--------------------------------------------------------
	def _get_variant_adr_subunit(self, data='?'):
		return self.__get_variant_adr_part(data = data, part = 'subunit')
	#--------------------------------------------------------
	def _get_variant_adr_location(self, data='?'):
		return self.__get_variant_adr_part(data = data, part = 'urb')
	#--------------------------------------------------------
	def _get_variant_adr_suburb(self, data='?'):
		return self.__get_variant_adr_part(data = data, part = 'suburb')
	#--------------------------------------------------------
	def _get_variant_adr_postcode(self, data='?'):
		return self.__get_variant_adr_part(data = data, part = 'postcode')
	#--------------------------------------------------------
	def _get_variant_adr_region(self, data='?'):
		return self.__get_variant_adr_part(data = data, part = 'l10n_region')
	#--------------------------------------------------------
	def _get_variant_adr_country(self, data='?'):
		return self.__get_variant_adr_part(data = data, part = 'l10n_country')
	#--------------------------------------------------------
	def _get_variant_patient_comm(self, data=None):
		comm_type = None
		template = '%(url)s'
		if data is not None:
			data_parts = data.split(self.__args_divider)
			if len(data_parts) > 0:
				comm_type = data_parts[0]
			if len(data_parts) > 1:
				template = data_parts[1]

		comms = self.pat.get_comm_channels(comm_medium = comm_type)
		if len(comms) == 0:
			if self.debug:
				return self._escape(_('no URL for comm channel [%s]') % data)
			return ''

		return template % comms[0].fields_as_dict(escape_style = self.__esc_style)
	#--------------------------------------------------------
	def _get_variant_patient_photo(self, data=None):

		template = '%s'
		target_mime = None
		target_ext = None
		if data is not None:
			parts = data.split(self.__args_divider)
			template = parts[0]
			if len(parts) > 1:
				target_mime = parts[1].strip()
			if len(parts) > 2:
				target_ext = parts[2].strip()
			if target_ext is None:
				if target_mime is not None:
					target_ext = gmMimeLib.guess_ext_by_mimetype(mimetype = target_mime)

		cache_key = 'patient_photo_path::%s::%s' % (target_mime, target_ext)
		try:
			fname = self.__cache[cache_key]
			_log.debug('cache hit on [%s]: %s', cache_key, fname)
		except KeyError:
			mugshot = self.pat.document_folder.latest_mugshot
			if mugshot is None:
				if self.debug:
					return self._escape(_('no mugshot available'))
				return ''
			fname = mugshot.save_to_file (
				target_mime = target_mime,
				target_extension = target_ext,
				ignore_conversion_problems = True
			)
			if fname is None:
				if self.debug:
					return self._escape(_('cannot export or convert latest mugshot'))
				return ''
			self.__cache[cache_key] = fname

		return template % fname

	#--------------------------------------------------------
	def _get_variant_patient_vcf(self, data):
		options = data.split(self.__args_divider)
		template = options[0].strip()
		if template == '':
			template = '%s'

		return template % self.pat.export_as_vcard()

	#--------------------------------------------------------
	def _get_variant_patient_mcf(self, data):
		kwds = {'tmpl': '%s', 'fmt': 'txt'}
		options = self._parse_ph_options (
			options_data = data,
			kwd_defaults = kwds
		)
		if options['fmt'] not in ['qr', 'mcf', 'txt']:
			if self.debug:
				return self._escape(_('patient_mcf: invalid format (qr/mcf/txt)'))
			return ''

		if options['fmt'] == 'txt':
			return options['tmpl'] % self._escape(self.pat.MECARD)

		if options['fmt'] == 'mcf':
			return options['tmpl'] % self.pat.export_as_mecard()

		if options['fmt'] == 'qr':
			qr_filename = gmTools.create_qrcode(text = self.pat.MECARD)
			if qr_filename is None:
				return self._escape('patient_mcf-cannot_create_QR_code')
			return options['tmpl'] % qr_filename

		return None

	#--------------------------------------------------------
	def _get_variant_patient_gdt(self, data):
		options = data.split(self.__args_divider)
		template = options[0].strip()
		if template == '':
			template = '%s'

		return template % self.pat.export_as_gdt()

	#--------------------------------------------------------
	def _get_variant_patient_tags(self, data='%s//\\n'):
		if len(self.pat.tags) == 0:
			if self.debug:
				return self._escape(_('no tags for this patient'))
			return ''

		tags = gmDemographicsWidgets.select_patient_tags(patient = self.pat)

		if tags is None:
			if self.debug:
				return self._escape(_('no patient tags selected for inclusion') % data)
			return ''

		template, separator = data.split('//', 2)

		return separator.join([ template % t.fields_as_dict(escape_style = self.__esc_style) for t in tags ])
#	#--------------------------------------------------------
#	def _get_variant_patient_tags_table(self, data=u'?'):
#		pass
	#--------------------------------------------------------
	# praxis related placeholders
	#--------------------------------------------------------
	def _get_variant_praxis(self, data=None):
		options = data.split(self.__args_divider)

		if 'select' in options:
			options.remove('select')
			branch = 'select branch'
		else:
			branch = gmPraxis.cPraxisBranch(aPK_obj = gmPraxis.gmCurrentPraxisBranch()['pk_praxis_branch'])

		template = '%s'
		if len(options) > 0:
			template = options[0]
		if template.strip() == '':
			template = '%s'

		return template % branch.fields_as_dict(escape_style = self.__esc_style)

	#--------------------------------------------------------
	def _get_variant_praxis_vcf(self, data=None):

		cache_key = 'current_branch_vcf_path'
		try:
			vcf_name = self.__cache[cache_key]
			_log.debug('cache hit (%s): [%s]', cache_key, vcf_name)
		except KeyError:
			vcf_name = gmPraxis.gmCurrentPraxisBranch().vcf
			self.__cache[cache_key] = vcf_name

		template = '%s'
		if data.strip() != '':
			template = data

		return template % vcf_name

	#--------------------------------------------------------
	def _get_variant_praxis_mcf(self, data):
		kwds = {'tmpl': '%s', 'fmt': 'txt'}
		options = self._parse_ph_options (
			options_data = data,
			kwd_defaults = kwds
		)
		if options['fmt'] not in ['qr', 'mcf', 'txt']:
			if self.debug:
				return self._escape(_('praxis_mcf: invalid format (qr/mcf/txt)'))
			return ''

		if options['fmt'] == 'txt':
			return options['tmpl'] % self._escape(gmPraxis.gmCurrentPraxisBranch().MECARD)

		if options['fmt'] == 'mcf':
			return options['tmpl'] % gmPraxis.gmCurrentPraxisBranch().export_as_mecard()

		if options['fmt'] == 'qr':
			qr_filename = gmTools.create_qrcode(text = gmPraxis.gmCurrentPraxisBranch().MECARD)
			if qr_filename is None:
				return self._escape('praxis_mcf-cannot_create_QR_code')
			return options['tmpl'] % qr_filename

		return None

	#--------------------------------------------------------
	def _get_variant_praxis_scan2pay(self, data):
		kwds = {'fmt': 'qr'}
		options = self._parse_ph_options (
			options_data = data,
			kwd_defaults = kwds
		)
		if options['fmt'] not in ['qr', 'txt']:
			if self.debug:
				return self._escape(_('praxis_scan2pay: invalid format (qr/txt)'))
			return ''

		data_str = gmPraxis.gmCurrentPraxisBranch().scan2pay_data
		if data_str is None:
			if self.debug:
				return self._escape('praxis_scan2pay-cannot_create_data_file')
			return ''

		if options['fmt'] == 'txt':
			return self._escape(data_str)
			#return template % self._escape(gmPraxis.gmCurrentPraxisBranch().MECARD)

		if options['fmt'] == 'qr':
			qr_filename = gmTools.create_qrcode(text = data_str)
			if qr_filename is None:
				if self.debug:
					return self._escape('praxis_scan2pay-cannot_create_QR_code')
				return ''
			#return template % qr_filename
			return qr_filename

		return None

	#--------------------------------------------------------
	def _get_variant_praxis_address(self, data=''):
		options = data.split(self.__args_divider)

		# formatting template
		template = _('%(street)s %(number)s, %(postcode)s %(urb)s, %(l10n_region)s, %(l10n_country)s')
		if len(options) > 0:
			if options[0].strip() != '':
				template = options[0]

		adr = gmPraxis.gmCurrentPraxisBranch().address
		if adr is None:
			if self.debug:
				return _('no address recorded')
			return ''
		try:
			return template % adr.fields_as_dict(escape_style = self.__esc_style)
		except Exception:
			_log.exception('error formatting address')
			_log.error('template: %s', template)

		return None

	#--------------------------------------------------------
	def _get_variant_praxis_comm(self, data=None):
		options = data.split(self.__args_divider)
		comm_type = options[0]
		template = '%(url)s'
		if len(options) > 1:
			template = options[1]

		comms = gmPraxis.gmCurrentPraxisBranch().get_comm_channels(comm_medium = comm_type)
		if len(comms) == 0:
			if self.debug:
				return self._escape(_('no URL for comm channel [%s]') % data)
			return ''

		return template % comms[0].fields_as_dict(escape_style = self.__esc_style)

	#--------------------------------------------------------
	def _get_variant_praxis_id(self, data=None):
		options = data.split(self.__args_divider)
		id_type = options[0].strip()
		if id_type == '':
			return self._escape('praxis external ID: type is missing')

		if len(options) > 1:
			issuer = options[1].strip()
			if issuer == '':
				issuer = None
		else:
			issuer = None

		if len(options) > 2:
			template = options[2]
		else:
			template = '%(name)s: %(value)s (%(issuer)s)'

		ids = gmPraxis.gmCurrentPraxisBranch().get_external_ids(id_type = id_type, issuer = issuer)
		if len(ids) == 0:
			if self.debug:
				return self._escape(_('no external ID [%s] by [%s]') % (id_type, issuer))
			return ''

		return template % self._escape_dict_like(dict_like = ids[0], none_string = '')

	#--------------------------------------------------------
	# provider related placeholders
	#--------------------------------------------------------
	def _get_variant_current_provider(self, data=None):
		prov = gmStaff.gmCurrentProvider()

		tmp = '%s%s. %s' % (
			gmTools.coalesce(prov['title'], '', '%s '),
			prov['firstnames'][:1],
			prov['lastnames']
		)
		return self._escape(tmp)

	#--------------------------------------------------------
	def _get_variant_current_provider_title(self, data=None):
		if data is None:
			data = u'%(title)s'
		elif data.strip() == u'':
			data = u'%(title)s'
		return self._get_variant_current_provider_name(data = data)

	#--------------------------------------------------------
	def _get_variant_current_provider_firstnames(self, data=None):
		if data is None:
			data = u'%(firstnames)s'
		elif data.strip() == u'':
			data = u'%(firstnames)s'
		return self._get_variant_current_provider_name(data = data)

	#--------------------------------------------------------
	def _get_variant_current_provider_lastnames(self, data=None):
		if data is None:
			data = u'%(lastnames)s'
		elif data.strip() == u'':
			data = u'%(lastnames)s'
		return self._get_variant_current_provider_name(data = data)

	#--------------------------------------------------------
	def _get_variant_current_provider_name(self, data=None):
		if data is None:
			return [_('template is missing')]
		if data.strip() == '':
			return [_('template is empty')]
		prov = gmStaff.gmCurrentProvider()
		name = prov.identity.get_active_name()
		parts = {
			'title': self._escape(gmTools.coalesce(name['title'], '')),
			'firstnames': self._escape(name['firstnames']),
			'lastnames': self._escape(name['lastnames']),
			'preferred': self._escape(gmTools.coalesce(name['preferred'], '')),
			'alias': self._escape(prov['short_alias'])
		}
		return data % parts

	#--------------------------------------------------------
	def _get_variant_current_provider_external_id(self, data=''):
		data_parts = data.split(self.__args_divider)
		if len(data_parts) < 2:
			return self._escape('current provider external ID: template is missing')

		id_type = data_parts[0].strip()
		if id_type == '':
			return self._escape('current provider external ID: type is missing')

		issuer = data_parts[1].strip()
		if issuer == '':
			return self._escape('current provider external ID: issuer is missing')

		prov = gmStaff.gmCurrentProvider()
		ids = prov.identity.get_external_ids(id_type = id_type, issuer = issuer)

		if len(ids) == 0:
			if self.debug:
				return self._escape(_('no external ID [%s] by [%s]') % (id_type, issuer))
			return ''

		return self._escape(ids[0]['value'])

	#--------------------------------------------------------
	def _get_variant_primary_praxis_provider(self, data=None):
		prov = self.pat.primary_provider
		if prov is None:
			return self._get_variant_current_provider()

		title = gmTools.coalesce (
			prov['title'],
			gmGender.map_gender2salutation(prov['gender'])
		)

		tmp = '%s %s. %s' % (
			title,
			prov['firstnames'][:1],
			prov['lastnames']
		)
		return self._escape(tmp)

	#--------------------------------------------------------
	def _get_variant_primary_praxis_provider_external_id(self, data=''):
		data_parts = data.split(self.__args_divider)
		if len(data_parts) < 2:
			return self._escape('primary in-praxis provider external ID: template is missing')

		id_type = data_parts[0].strip()
		if id_type == '':
			return self._escape('primary in-praxis provider external ID: type is missing')

		issuer = data_parts[1].strip()
		if issuer == '':
			return self._escape('primary in-praxis provider external ID: issuer is missing')

		prov = self.pat.primary_provider
		if prov is None:
			if self.debug:
				return self._escape(_('no primary in-praxis provider'))
			return ''

		ids = prov.identity.get_external_ids(id_type = id_type, issuer = issuer)

		if len(ids) == 0:
			if self.debug:
				return self._escape(_('no external ID [%s] by [%s]') % (id_type, issuer))
			return ''

		return self._escape(ids[0]['value'])

	#--------------------------------------------------------
	def _get_variant_external_id(self, data=''):
		data_parts = data.split(self.__args_divider)
		if len(data_parts) < 2:
			return self._escape('patient external ID: template is missing')

		id_type = data_parts[0].strip()
		if id_type == '':
			return self._escape('patient external ID: type is missing')

		issuer = data_parts[1].strip()
		if issuer == '':
			return self._escape('patient external ID: issuer is missing')

		ids = self.pat.get_external_ids(id_type = id_type, issuer = issuer)

		if len(ids) == 0:
			if self.debug:
				return self._escape(_('no external ID [%s] by [%s]') % (id_type, issuer))
			return ''

		return self._escape(ids[0]['value'])

	#--------------------------------------------------------
	def _get_variant_allergy_state(self, data=None):
		state = self.pat.emr.allergy_state
		if not state:
			return self._escape(_('unobtained'))

		date_confirmed = ''
		if state['last_confirmed']:
			date_confirmed = ' (%s)' % state['last_confirmed'].strftime('%Y %B %d')
		return self._escape('%s%s' % (state.state_string, date_confirmed))

	#--------------------------------------------------------
	def _get_variant_allergy_list(self, data=None):
		if data is None:
			return self._escape(_('template is missing'))

		template, separator = data.split('//', 2)

		return separator.join([ template % a.fields_as_dict(date_format = '%Y %b %d', escape_style = self.__esc_style) for a in self.pat.emr.get_allergies() ])

	#--------------------------------------------------------
	def _get_variant_allergies(self, data=None):

		if data is None:
			return self._escape(_('template is missing'))

		return '\n'.join([ data % a.fields_as_dict(date_format = '%Y %b %d', escape_style = self.__esc_style) for a in self.pat.emr.get_allergies() ])

	#--------------------------------------------------------
	def _get_variant_current_meds_AMTS_enhanced(self, data=None):
		return self._get_variant_current_meds_AMTS(data = data, strict = False)

	#--------------------------------------------------------
	def _get_variant_current_meds_AMTS(self, data=None, strict:bool=True) -> str:
		# select intakes
		emr = self.pat.emr
		from Gnumed.wxpython import gmSubstanceIntakeWidgets
		intakes2export = gmSubstanceIntakeWidgets.manage_substance_intakes(emr = emr)
		if not intakes2export:
			return ''

		# create data files / datamatrix code files
		self.__create_amts_datamatrix_files(intakes = intakes2export)
		# create AMTS-LaTeX per intake
		intake_as_latex_rows = []
		for intake in intakes2export:
			intake_as_latex_rows.append(intake._get_as_amts_latex(strict = strict))
		del intakes2export
		# append allergy information
		# - state
		intake_as_latex_rows.extend(emr.allergy_state._get_as_amts_latex(strict = strict))
		# - allergies
		for allg in emr.get_allergies():
			intake_as_latex_rows.append(allg._get_as_amts_latex(strict = strict))
		# insert \newpage after each group of 15 rows
		table_rows = intake_as_latex_rows[:15]
		if len(intake_as_latex_rows) > 15:
			table_rows.append('\\newpage')
			table_rows.extend(intake_as_latex_rows[15:30])
		if len(intake_as_latex_rows) > 30:
			table_rows.append('\\newpage')
			table_rows.extend(intake_as_latex_rows[30:45])
		if strict:
			return '\n'.join(table_rows)

		# allow two more pages in enhanced mode
		if len(intake_as_latex_rows) > 45:
			table_rows.append('\\newpage')
			table_rows.extend(intake_as_latex_rows[45:60])
		if len(intake_as_latex_rows) > 60:
			table_rows.append('\\newpage')
			table_rows.extend(intake_as_latex_rows[60:75])
		return '\n'.join(table_rows)

	#--------------------------------------------------------
	def __create_amts_datamatrix_files(self, intakes=None):

		# setup dummy files
		for idx in [1,2,3]:
			self.set_placeholder(key = 'amts_data_file_%s' % idx, value = './missing-file.txt', known_only = False)
			self.set_placeholder(key = 'amts_png_file_%s' % idx, value = './missing-file.png', known_only = False)
		self.set_placeholder(key = 'amts_png_file_current_page', value = './missing-file-current-page.png', known_only = False)
		self.set_placeholder(key = 'amts_png_file_utf8', value = './missing-file-utf8.png', known_only = False)
		self.set_placeholder(key = 'amts_data_file_utf8', value = './missing-file-utf8.txt', known_only = False)

		# find processor
		found, dmtx_creator = gmShellAPI.detect_external_binary(binary = 'gm-create_datamatrix')
		_log.debug(dmtx_creator)
		if not found:
			_log.error('gm-create_datamatrix(.bat/.exe) not found')
			return

		png_dir = gmTools.mk_sandbox_dir()
		_log.debug('sandboxing AMTS datamatrix PNGs in: %s', png_dir)

		from Gnumed.business import gmForms

		# generate GNUmed-enhanced non-conformant data file and datamatrix
		# for embedding (utf8, unabridged data fields)
		amts_data_template_def_file = gmMedication.generate_amts_data_template_definition_file(strict = False)
		_log.debug('amts data template definition file: %s', amts_data_template_def_file)
		form = gmForms.cTextForm(template_file = amts_data_template_def_file)
		# <S>ection with intakes</S>
		amts_sections = '<S>%s</S>' % ''.join ([
			i._get_as_amts_data(strict = False) for i in intakes
		])
		# <S>ection with allergy data</S>
		emr = self.pat.emr
		amts_sections += emr.allergy_state._get_as_amts_data(strict = False) % ''.join ([
			a._get_as_amts_data(strict = False) for a in emr.get_allergies()
		])
		self.set_placeholder(key = 'amts_intakes_as_data_enhanced', value = amts_sections, known_only = False)
#		self.set_placeholder(key = u'amts_check_symbol', value = gmMedication.calculate_amts_data_check_symbol(intakes = intakes), known_only = False)
		self.set_placeholder(key = 'amts_total_pages', value = '1', known_only = False)
		success = form.substitute_placeholders(data_source = self)
		self.unset_placeholder(key = 'amts_intakes_as_data_enhanced')
#		self.unset_placeholder(key = u'amts_check_symbol')
		self.unset_placeholder(key = 'amts_total_pages')
		if not success:
			_log.error('cannot substitute into amts data file form template')
			return
		data_file = form.re_editable_filenames[0]
		png_file = os.path.join(png_dir, 'gm4amts-datamatrix-utf8.png')
		cmd = '%s %s %s' % (dmtx_creator, data_file, png_file)
		success = gmShellAPI.run_command_in_shell(command = cmd, blocking = True)
		if not success:
			_log.error('error running [%s]' % cmd)
			return
		self.set_placeholder(key = 'amts_data_file_utf8', value = data_file, known_only = False)
		self.set_placeholder(key = 'amts_png_file_utf8', value = png_file, known_only = False)

		# generate conformant per-page files:
		total_pages = (len(intakes) / 15.0)
		if total_pages > int(total_pages):
			total_pages += 1
		total_pages = int(total_pages)
		_log.debug('total pages: %s', total_pages)

		png_file_base = os.path.join(png_dir, 'gm4amts-datamatrix-page-')
		for this_page in range(1,total_pages+1):
			intakes_this_page = intakes[(this_page-1)*15:this_page*15]
			amts_data_template_def_file = gmMedication.generate_amts_data_template_definition_file(strict = True)
			_log.debug('amts data template definition file: %s', amts_data_template_def_file)
			form = gmForms.cTextForm(template_file = amts_data_template_def_file)
			# <S>ection with intakes</S>
			amts_sections = '<S>%s</S>' % ''.join ([
				i._get_as_amts_data(strict = False) for i in intakes_this_page
			])
			if this_page == total_pages:
				# <S>ection with allergy data</S>
				emr = self.pat.emr
				amts_sections += emr.allergy_state._get_as_amts_data(strict = False) % ''.join ([
					a._get_as_amts_data(strict = False) for a in emr.get_allergies()
				])
			self.set_placeholder(key = 'amts_intakes_as_data', value = amts_sections, known_only = False)
#			self.set_placeholder(key = u'amts_check_symbol', value = gmMedication.calculate_amts_data_check_symbol(intakes = intakes_this_page), known_only = False)
			if total_pages == 1:
				pg_idx = ''
			else:
				pg_idx = '%s' % this_page
			self.set_placeholder(key = 'amts_page_idx', value = pg_idx, known_only = False)
			self.set_placeholder(key = 'amts_total_pages', value = '%s' % total_pages, known_only = False)
			success = form.substitute_placeholders(data_source = self)
			self.unset_placeholder(key = 'amts_intakes_as_data')
#			self.unset_placeholder(key = u'amts_check_symbol')
			self.unset_placeholder(key = 'amts_page_idx')
			self.unset_placeholder(key = 'amts_total_pages')
			if not success:
				_log.error('cannot substitute into amts data file form template')
				return

			data_file = form.re_editable_filenames[0]
			png_file = '%s%s.png' % (png_file_base, this_page)
			latin1_data_file = gmTools.recode_file (
				source_file = data_file,
				source_encoding = 'utf8',
				target_encoding = 'latin1',
				base_dir = os.path.split(data_file)[0]
			)
			cmd = '%s %s %s' % (dmtx_creator, latin1_data_file, png_file)
			success = gmShellAPI.run_command_in_shell(command = cmd, blocking = True)
			if not success:
				_log.error('error running [%s]' % cmd)
				return

			# cache file names for later use in \embedfile
			self.set_placeholder(key = 'amts_data_file_%s' % this_page, value = latin1_data_file, known_only = False)
			self.set_placeholder(key = 'amts_png_file_%s' % this_page, value = png_file, known_only = False)

		self.set_placeholder(key = 'amts_png_file_current_page', value = png_file_base + '\\thepage', known_only = False)

	#--------------------------------------------------------
	def _get_variant_current_meds_for_rx(self, data=None):
		if data is None:
			return self._escape(_('current_meds_for_rx: template is missing'))

		emr = self.pat.emr
		from Gnumed.wxpython import gmSubstanceIntakeWidgets
		current_meds = gmSubstanceIntakeWidgets.manage_substance_intakes(emr = emr)
		if current_meds is None:
			return ''

		intakes2show = {}
		for intake in current_meds:
			fields_dict = intake.fields_as_dict(date_format = '%Y %b %d', escape_style = self.__esc_style)
			fields_dict['medically_formatted_start'] = self._escape(intake.medically_formatted_start)
			if intake['pk_drug_product'] is None:
				fields_dict['product'] = self._escape(_('generic %s') % fields_dict['substance'])
				fields_dict['contains'] = self._escape('%s %s%s' % (fields_dict['substance'], fields_dict['amount'], fields_dict['unit']))
				intakes2show[fields_dict['product']] = fields_dict
			else:
				comps = [ c.split('::') for c in intake.containing_drug['components'] ]
				fields_dict['contains'] = self._escape('; '.join([ '%s %s%s' % (c[0], c[1], c[2]) for c in comps ]))
				intakes2show[intake['product']] = fields_dict		# this will make multi-component drugs unique

		intakes2dispense = {}
		for product, intake in intakes2show.items():
			msg = _('Dispense how much/many of "%(product)s (%(contains)s)" ?') % intake
			amount2dispense = wx.GetTextFromUser(msg, _('Amount to dispense ?'))
			if amount2dispense == '':
				continue
			intake['amount2dispense'] = amount2dispense
			intakes2dispense[product] = intake

		return '\n'.join([ data % intake for intake in intakes2dispense.values() ])

	#--------------------------------------------------------
	def _get_variant_substance_abuse(self, data=None):
		if data is None:
			return self._escape(_('template is missing'))
		template = data
		from Gnumed.wxpython import gmHabitWidgets
		abuses = gmHabitWidgets.manage_substance_abuse(patient = self.pat)
		if abuses is None:
			return ''
		lines = []
		for a in abuses:
			fields = a.fields_as_dict(date_format = '%Y %b %d', escape_style = self.__esc_style)
			fields['use_type'] = a.use_type_string
			lines.append(template % fields)
		return '\n'.join(lines)

	#--------------------------------------------------------
	def _get_variant_current_meds(self, data=None):

		if data is None:
			return self._escape(_('template is missing'))

		parts = data.split(self.__args_divider)
		template = parts[0]
		ask_user = False
		if len(parts) > 1:
			ask_user = (parts[1] == 'select')

		emr = self.pat.emr
		if ask_user:
			from Gnumed.wxpython import gmSubstanceIntakeWidgets
			current_meds = gmSubstanceIntakeWidgets.manage_substance_intakes(emr = emr)
			if current_meds is None:
				return ''
		else:
			current_meds = emr.get_current_medications (
				include_inactive = False,
				order_by = 'product, substance'
			)
			if len(current_meds) == 0:
				return ''

		lines = []
		for m in current_meds:
			data = m.fields_as_dict(date_format = '%Y %b %d', escape_style = self.__esc_style)
			data['medically_formatted_start'] = self._escape(m.medically_formatted_start)
			lines.append(template % data)

		return '\n'.join(lines)
	#--------------------------------------------------------
	def _get_variant_current_meds_table(self, data=None):
		return gmMedication.format_substance_intake (
			emr = self.pat.emr,
			output_format = self.__esc_style,
			table_type = 'by-product'
		)
	#--------------------------------------------------------
	def _get_variant_current_meds_notes(self, data=None):
		return gmMedication.format_substance_intake_notes (
			emr = self.pat.emr,
			output_format = self.__esc_style,
			table_type = 'by-product'
		)
	#--------------------------------------------------------
	def _get_variant_lab_table(self, data=None):
		return gmPathLab.format_test_results (
			results = self.pat.emr.get_test_results_by_date(),
			output_format = self.__esc_style
		)

	#--------------------------------------------------------
	def _get_variant_test_results(self, data=None):

		template = ''
		date_format = '%Y %b %d %H:%M'
		separator = '\n'
		options = data.split(self.__args_divider)
		try:
			template = options[0].strip()
			date_format = options[1]
			separator = options[2]
		except IndexError:
			pass

		if date_format.strip() == '':
			date_format = '%Y %b %d %H:%M'
		if separator.strip() == '':
			separator = '\n'

		from Gnumed.wxpython.gmMeasurementWidgets import manage_measurements
		results = manage_measurements(single_selection = False, emr = self.pat.emr)
		if results is None:
			if self.debug:
				return self._escape(_('no results for this patient (available or selected)'))
			return ''

		if template == '':
			return (separator + separator).join([ self._escape(r.format(date_format = date_format)) for r in results ])

		return separator.join([ template % r.fields_as_dict(date_format = date_format, escape_style = self.__esc_style) for r in results ])

	#--------------------------------------------------------
	def _get_variant_most_recent_test_results(self, data=None):
		most_recent = gmPathLab.get_most_recent_result_for_test_types (
			pk_test_types = None,			# we want most recent results for *all* tests
			pk_patient = self.pat.ID,
			consider_meta_type = True,
			order_by = 'unified_name'
		)
		if len(most_recent) == 0:
			if self.debug:
				return self._escape(_('no results for this patient available'))
			return ''

		from Gnumed.wxpython.gmMeasurementWidgets import manage_measurements
		results2show = manage_measurements (
			single_selection = False,
			measurements2manage = most_recent,
			message = _('Most recent results: select the ones to include')
		)
		if results2show is None:
			if self.debug:
				return self._escape(_('no results for this patient selected'))
			return ''

		kwds = {'tmpl': '', 'dfmt': '%Y %b %d', 'sep': '\n'}
		options = self._parse_ph_options (
			options_data = data,
			kwd_defaults = kwds
		)
		if options['tmpl'] == '':
			return (options['sep'] + options['sep']).join([ self._escape(r.format(date_format = options['dfmt'])) for r in results2show ])

		return options['sep'].join([ options['tmpl'] % r.fields_as_dict(date_format = options['dfmt'], escape_style = self.__esc_style) for r in results2show ])

	#--------------------------------------------------------
	def _get_variant_latest_vaccs_table(self, data=None):
		return gmVaccination.format_latest_vaccinations (
			output_format = self.__esc_style,
			emr = self.pat.emr
		)
	#--------------------------------------------------------
	def _get_variant_vaccination_history(self, data=None):
		options = data.split(self.__args_divider)
		template = options[0]
		if len(options) > 1:
			date_format = options[1]
		else:
			date_format = '%Y %b %d'
		vaccinations_as_dict = []
		for v in self.pat.emr.get_vaccinations(order_by = 'date_given DESC, vaccine'):
			v_as_dict = v.fields_as_dict(date_format = date_format, escape_style = self.__esc_style)
			v_as_dict['l10n_indications'] = [ ind['l10n_indication'] for ind in v['indications'] ]
			vaccinations_as_dict.append(v_as_dict)

		return u'\n'.join([ template % v for v in vaccinations_as_dict ])

	#--------------------------------------------------------
	def _get_variant_PHX(self, data=None):

		if data is None:
			if self.debug:
				_log.error('PHX: missing placeholder arguments')
				return self._escape(_('PHX: Invalid placeholder options.'))
			return ''

		_log.debug('arguments: %s', data)

		data_parts = data.split(self.__args_divider)
		template = '%s'
		separator = '\n'
		date_format = '%Y %b %d'
		try:
			template = data_parts[0]
			separator = data_parts[1]
			date_format = data_parts[2]
		except IndexError:
			pass

		phxs = gmEMRStructWidgets.select_health_issues(emr = self.pat.emr)
		if phxs is None:
			if self.debug:
				return self._escape(_('no PHX for this patient (available or selected)'))
			return ''

		return separator.join ([
			template % phx.fields_as_dict (
				date_format = date_format,
				escape_style = self.__esc_style,
				bool_strings = (self._escape(_('yes')), self._escape(_('no')))
			) for phx in phxs
		])

	#--------------------------------------------------------
	def _get_variant_problems(self, data=None):

		if data is None:
			return self._escape(_('template is missing'))
		probs = self.pat.emr.get_problems()
		return '\n'.join([ data % p.fields_as_dict(date_format = '%Y %b %d', escape_style = self.__esc_style) for p in probs ])

	#--------------------------------------------------------
	def _get_variant_diagnoses(self, data=None):

		if data is None:
			return self._escape(_('template is missing'))

		template = data
		dxs = self.pat.emr.candidate_diagnoses
		if len(dxs) == 0:
			_log.debug('no diagnoses available')
			return ''

		selected = gmListWidgets.get_choices_from_list (
			msg = _('Select the relevant diagnoses:'),
			caption = _('Diagnosis selection'),
			columns = [ _('Diagnosis'), _('Marked confidential'), _('Certainty'), _('Source') ],
			choices = [[
				dx['diagnosis'],
				gmTools.bool2subst(dx['explicitely_confidential'], _('yes'), _('no'), _('unknown')),
				gmTools.coalesce(dx['diagnostic_certainty_classification'], ''),
				dx['source']
				] for dx in dxs
			],
			data = dxs,
			single_selection = False,
			can_return_empty = True
		)
		if selected is None:
			_log.debug('user did not select any diagnoses')
			return ''

		if len(selected) == 0:
			_log.debug('user did not select any diagnoses')
			return ''
			#return template % {'diagnosis': u'', 'diagnostic_certainty_classification': u''}

		return '\n'.join(template % self._escape_dict_like(dx, none_string = '?', bool_strings = [_('yes'), _('no')]) for dx in selected)

	#--------------------------------------------------------
	def _get_variant_today(self, data=None):
		if not data:
			data = '%Y %b %d'
		return self._escape(gmDateTime.pydt_now_here().strftime(data))

	#--------------------------------------------------------
	def _get_variant_tex_escape(self, data=None):
		return gmTools.tex_escape_string(text = data)

	#--------------------------------------------------------
	def _get_variant_url_escape(self, data=None):
		return self._escape(urllib.parse.quote(data.encode('utf8')))

	#--------------------------------------------------------
	def _get_variant_text_snippet(self, data=None):
		data_parts = data.split(self.__args_divider)
		keyword = data_parts[0]
		template = '%s'
		if len(data_parts) > 1:
			template = data_parts[1]
		expansion = gmKeywordExpansionWidgets.expand_keyword(keyword = keyword, show_list_if_needed = True)
		if expansion is None:
			if self.debug:
				return self._escape(_('no textual expansion found for keyword <%s>') % keyword)
			return ''

		#return template % self._escape(expansion)
		return template % expansion

	#--------------------------------------------------------
	def _get_variant_data_snippet(self, data=None):
		parts = data.split(self.__args_divider)
		keyword = parts[0]
		template = '%s'
		target_mime = None
		target_ext = None
		if len(parts) > 1:
			template = parts[1]
		if len(parts) > 2:
			if parts[2].strip() != '':
				target_mime = parts[2].strip()
		if len(parts) > 3:
			if parts[3].strip() != '':
				target_ext = parts[3].strip()

		expansion = gmKeywordExpansion.get_expansion (
			keyword = keyword,
			textual_only = False,
			binary_only = True
		)
		if expansion is None:
			if self.debug:
				return self._escape(_('no binary expansion found for keyword <%s>') % keyword)
			return ''

		saved_fname = expansion.save_to_file()
		if saved_fname is None:
			if self.debug:
				return self._escape(_('cannot export data of binary expansion keyword <%s>') % keyword)
			return ''

		if expansion['is_encrypted']:
			saved_fname = gmCrypto.gpg_decrypt_file(filename = saved_fname)
			if saved_fname is None:
				if self.debug:
					return self._escape(_('cannot decrypt data of binary expansion keyword <%s>') % keyword)
				return ''

		if target_mime is None:
			return template % saved_fname

		converted_fname = gmMimeLib.convert_file(filename = saved_fname, target_mime = target_mime, target_extension = target_ext)
		if converted_fname is None:
			if self.debug:
				return self._escape(_('cannot convert data of binary expansion keyword <%s>') % keyword)
			# hoping that the target can cope:
			return template % saved_fname

		return template % converted_fname

	#--------------------------------------------------------
	def _get_variant_qrcode(self, data=None):
		options = data.split(self.__args_divider)
		if len(options) == 0:
			return None
		text4qr = options[0]
		if len(options) > 1:
			template = options[1]
		else:
			template = u'%s'
		qr_filename = gmTools.create_qrcode(text = text4qr)
		if qr_filename is None:
			return self._escape('cannot_create_QR_code')

		return template % qr_filename

	#--------------------------------------------------------
	def _get_variant_range_of(self, data=None):
		if data is None:
			return None
		# wrapper code already takes care of actually
		# selecting the range so all we need to do here
		# is to return the data itself
		return data

	#--------------------------------------------------------
	def _get_variant_yes_no(self, data=None):
		if data is None:
			return None

		msg, yes_txt, no_txt = self._parse_ph_options (
			options_data = data,
			kwd_defaults = {'msg': None, 'yes': None, 'no': ''}
		)
		if None in [msg, yes_txt]:
			return self._escape('YES_NO lacks proper definition')

		yes = gmGuiHelpers.gm_show_question(question = msg, cancel_button = False, title = 'Placeholder question')
		if yes:
			return self._escape(yes_txt)

		return self._escape(no_txt)

	#--------------------------------------------------------
	def _get_variant_if_not_empty(self, data=None):
		if data is None:
			return None

		parts = data.split(self.__args_divider)
		if len(parts) < 3:
			return 'IF_NOT_EMPTY lacks <instead> definition'
		txt = parts[0]
		template = parts[1]
		instead = parts[2]

		if txt.strip() == '':
			return instead
		if '%s' in template:
			return template % txt
		return template

	#--------------------------------------------------------
	def _get_variant_if_debugging(self, data=None):

		if data is None:
			return None
		parts = data.split(self.__args_divider)
		if len(parts) < 2:
			return self._escape(u'IF_DEBUGGING lacks proper definition')
		debug_str = parts[0]
		non_debug_str = parts[1]
		if self.debug:
			return debug_str
		return non_debug_str

	#--------------------------------------------------------
	def _get_variant_free_text(self, data=None):

		if data is None:
			parts = []
			msg = _('generic text')
			cache_key = 'free_text::%s' % datetime.datetime.now()
		else:
			parts = data.split(self.__args_divider)
			msg = parts[0]
			cache_key = 'free_text::%s' % msg

		try:
			return self.__cache[cache_key]
		except KeyError:
			pass

		if len(parts) > 1:
			preset = parts[1]
		else:
			preset = ''

		dlg = gmGuiHelpers.cMultilineTextEntryDlg (
			None,
			-1,
			title = _('Replacing <free_text> placeholder'),
			msg = _('Below you can enter free text.\n\n [%s]') % msg,
			text = preset
		)
		dlg.enable_user_formatting = True
		decision = dlg.ShowModal()
		text = dlg.value.strip()
		is_user_formatted = dlg.is_user_formatted
		dlg.DestroyLater()

		if decision != wx.ID_SAVE:
			if self.debug:
				return self._escape(_('Text input cancelled by user.'))
			return self._escape('')

		# user knows "best"
		if is_user_formatted:
			self.__cache[cache_key] = text
			return text

		text = self._escape(text)
		self.__cache[cache_key] = text
		return text

	#--------------------------------------------------------
	def _get_variant_bill(self, data=None):
		try:
			bill = self.__cache['bill']
		except KeyError:
			from Gnumed.wxpython import gmBillingWidgets
			bill = gmBillingWidgets.manage_bills(patient = self.pat)
			if bill is None:
				if self.debug:
					return self._escape(_('no bill selected'))
				return ''
			self.__cache['bill'] = bill

		parts = data.split(self.__args_divider)
		template = parts[0]
		if len(parts) > 1:
			date_format = parts[1]
		else:
			date_format = '%Y %B %d'

		return template % bill.fields_as_dict(date_format = date_format, escape_style = self.__esc_style)

	#--------------------------------------------------------
	def _get_variant_bill_scan2pay(self, data=None):
		try:
			bill = self.__cache['bill']
		except KeyError:
			from Gnumed.wxpython import gmBillingWidgets
			bill = gmBillingWidgets.manage_bills(patient = self.pat)
			if bill is None:
				if self.debug:
					return self._escape(_('no bill selected'))
				return ''
			self.__cache['bill'] = bill

		kwds = {'fmt': 'qr'}
		options = self._parse_ph_options (
			options_data = data,
			kwd_defaults = kwds
		)
		format = options['fmt']
		if format not in ['qr', 'txt']:
			if self.debug:
				return self._escape(_('praxis_scan2pay: invalid format (qr/txt)'))
			return ''

		from Gnumed.business import gmBilling
		data_str = gmBilling.get_scan2pay_data (
			gmPraxis.gmCurrentPraxisBranch(),
			bill,
			provider = gmStaff.gmCurrentProvider()
		)
		if data_str is None:
			if self.debug:
				return self._escape('bill_scan2pay-cannot_create_data_file')
			return ''

		if format == 'txt':
			return self._escape(data_str)

		if format == 'qr':
			qr_filename = gmBilling.generate_scan2pay_qrcode(data = data_str)
			if qr_filename is not None:
				return qr_filename

			if self.debug:
				return self._escape('bill_scan2pay-cannot_create_QR_code')

			return ''

		return None

	#--------------------------------------------------------
	def _get_variant_bill_item(self, data=None):
		try:
			bill = self.__cache['bill']
		except KeyError:
			from Gnumed.wxpython import gmBillingWidgets
			bill = gmBillingWidgets.manage_bills(patient = self.pat)
			if bill is None:
				if self.debug:
					return self._escape(_('no bill selected'))
				return ''
			self.__cache['bill'] = bill

		parts = data.split(self.__args_divider)
		template = parts[0]
		if len(parts) > 1:
			date_format = parts[1]
		else:
			date_format = '%Y %B %d'

		return '\n'.join([ template % i.fields_as_dict(date_format = date_format, escape_style = self.__esc_style) for i in bill.bill_items ])

	#--------------------------------------------------------
	def __get_variant_bill_adr_part(self, data=None, part=None):
		try:
			bill = self.__cache['bill']
		except KeyError:
			from Gnumed.wxpython import gmBillingWidgets
			bill = gmBillingWidgets.manage_bills(patient = self.pat)
			if bill is None:
				if self.debug:
					return self._escape(_('no bill selected'))
				return ''
			self.__cache['bill'] = bill
			self.__cache['bill-adr'] = bill.address

		try:
			bill_adr = self.__cache['bill-adr']
		except KeyError:
			bill_adr = bill.address
			self.__cache['bill-adr'] = bill_adr

		if bill_adr is None:
			if self.debug:
				return self._escape(_('[%s] bill has no address') % part)
			return ''

		if bill_adr[part] is None:
			return self._escape('')

		if data is None:
			return self._escape(bill_adr[part])

		if data == '':
			return self._escape(bill_adr[part])

		return data % self._escape(bill_adr[part])

	#--------------------------------------------------------
	def _get_variant_bill_adr_street(self, data='?'):
		return self.__get_variant_bill_adr_part(data = data, part = 'street')

	#--------------------------------------------------------
	def _get_variant_bill_adr_number(self, data='?'):
		return self.__get_variant_bill_adr_part(data = data, part = 'number')

	#--------------------------------------------------------
	def _get_variant_bill_adr_subunit(self, data='?'):
		return self.__get_variant_bill_adr_part(data = data, part = 'subunit')
	#--------------------------------------------------------
	def _get_variant_bill_adr_location(self, data='?'):
		return self.__get_variant_bill_adr_part(data = data, part = 'urb')

	#--------------------------------------------------------
	def _get_variant_bill_adr_suburb(self, data='?'):
		return self.__get_variant_bill_adr_part(data = data, part = 'suburb')

	#--------------------------------------------------------
	def _get_variant_bill_adr_postcode(self, data='?'):
		return self.__get_variant_bill_adr_part(data = data, part = 'postcode')

	#--------------------------------------------------------
	def _get_variant_bill_adr_region(self, data='?'):
		return self.__get_variant_bill_adr_part(data = data, part = 'l10n_region')

	#--------------------------------------------------------
	def _get_variant_bill_adr_country(self, data='?'):
		return self.__get_variant_bill_adr_part(data = data, part = 'l10n_country')

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def _parse_ph_options__old(self, option_defs:dict=None, options_string:str=None, ignore_positional_options:bool=True) -> tuple:
		"""Parse a string for options and values.

		Options must be separated by *self.__args_divider*.

		Each option must be of the form 'name=value', where
		value _can_ contain more '='s.

		If an option does not contain a '=' it is considered
		a _positional_ option and possibly returned as-is.

		Args:
			option_defs: {'option name in placeholder string': 'default value for option', ...}
				It _can_ contain a key __legacy_options__ which will be filled
				with positional options in the order they are found, if any.
			options_str: the text to parse for option values
			ignore_positional_options: whether or not to return any positional (non-keyword) options found

		Returns:
			A tuple of values in the order of option_defs -> keys. The
			caller can rely on order and count.

			If *ignore_positional_options* is False
			positional options will be included in the
			result as a (possibly empty) list.

			If *option_defs* contains a keyword
			__legacy_options__ the positional options list
			will be returned at that position within the
			result, else the list will be appended to the end
			of the results.
		"""
		assert (option_defs is not None), '<option_defs> must not be None'
		assert (options_string is not None), '<options_string> must not be None'
		if ignore_positional_options and ('__legacy_options__' in option_defs):
			raise AssertionError("<ignore_positional_options>=True but '__legacy_options__' found in <option_defs>")
		_log.debug('option defaults: %s', option_defs)
		_log.debug('options: %s', options_string)
		legacy_options = []
		options2return = option_defs.copy()
		if options_string.strip() == '':
			return tuple([ options2return[o_name] for o_name in options2return.keys() ])

		if '=' not in options_string:
			return tuple([ 'invalid param fmt' for o_name in options2return.keys() ])

		options = options_string.split(self.__args_divider)
		for opt in options:
			opt_parts = opt.split('=', 1)
			if len(opt_parts) == 1:
				_log.warning('[%s] -> legacy positional option', opt)
				legacy_options.append(opt_parts[0])
				continue
			opt_name = opt_parts[0].strip()
			if opt_name not in option_defs:
				# if we would not ignore this option - as seems
				# tempting since the definition itself is fully
				# valid - we would expand the result tuple beyond
				# what is expected by the caller, thusly risking
				# an exception upstream
				_log.warning('[%s] -> unexpected kwd option, ignoring', opt_name)
				continue
			options2return[opt_name] = opt_parts[1]
			_log.debug('[%s] -> kwd option, value [%s]', opt, opt_parts[1])
		if ignore_positional_options:
			_log.warning('ignoring legacy positional options, if any: %s', legacy_options)
		else:
			_log.debug('legacy positional options found: %s', legacy_options)
			options2return['__legacy_options__'] = legacy_options
		_log.debug('options found: %s', options2return)
		return tuple([ options2return[o_name] for o_name in options2return ])

	#--------------------------------------------------------
	def _parse_ph_options(self, options_data:str=None, switch_defaults:dict=None, kwd_defaults:dict=None, pos_defaults:dict=None) -> dict:
		"""Parse a string for options and values.

		Options must be separated by *self.__args_divider*.

		Option types:

			Switches: Options which by their existence toggle their default. Think _select_, _display_, or _verbose_.

			Keywords: Must contain an option name, followed by a '=', followed by a value. Think 'template=%s'. The value _can_ contain more '='s.

			Positionals: Options which contain only a value. Their name is defined by their _position_ within the options data.

		Note:
			* Positional defaults override keyword defaults override switch defaults of the same name.

			* Given switches override keyword defaults of the same name.

			* Given keyword values override switches (given or default) of the same name.

			* Unexpected keywords (not in *kwd_defaults*) are considered positionals.

			* Given positionals override keyword/switches (given or default) of the same name.

		Args:
			options_data: The text to parse for options and values.
			switch_defaults: Defaults for switch options. All options to be detected as switches must be listed here.
			kwd_defaults: Defaults for keyword options. Example: {'option name in placeholder string': 'default value for option', ...}.
			pos_defaults: Defaults for positional options. The keys define the option names. Values will be taken from the options data, or from the defaults.

		Returns:

			A dictionary containing all the defined options
			and their values. Values come from either the
			options data, or else their defined defaults.

			Unaccounted-for options are returned as a
			(possibly empty) list under the name
			'__undefined_options__'.
		"""
		assert (options_data is not None), '<options_data> must not be None'
		_log.debug('parsing for option values: [%s]', options_data)
		options2return = {}
		if switch_defaults:
			options2return.update(switch_defaults)
		if kwd_defaults:
			options2return.update(kwd_defaults)
		if pos_defaults:
			options2return.update(pos_defaults)
		options2return['__undefined_options__'] = []
		if options_data.strip() == '':
			_log.debug('returning defaults')
			return options2return

		options_given = options_data.split(self.__args_divider)
		_log.debug('options: %s', options_given)

		if switch_defaults:
			_log.debug('switches: %s', switch_defaults)
			for switch in switch_defaults:
				if switch in options_given:
					options2return[switch] = not switch_defaults[switch]
					options_given.remove(switch)
				_log.debug('switch [%s]: default [%s], value [%s]', switch, switch_defaults[switch], options2return[switch])
		_log.debug('options after switch parsing: %s', options_given)

		if kwd_defaults:
			_log.debug('kwds: %s', kwd_defaults)
			for opt in options_given.copy():
				opt_parts = opt.split('=', 1)
				if len(opt_parts) == 1:
					# positional non-switch option, skip for later
					continue
				opt_name = opt_parts[0].strip()
				if opt_name not in kwd_defaults:
					#_log.warning('kwd option [%s] -> unexpected, skipping', opt)
					# potentially positional non-switch option containing a '=' by happenstance, skip for later
					continue
				options2return[opt_name] = opt_parts[1]
				options_given.remove(opt)
		_log.debug('options after kwds parsing: %s', options_given)

		remaining_positionals = options_given.copy()
		if pos_defaults:
			_log.debug('positionals: %s', pos_defaults)
			positionals_names = list(pos_defaults.keys())
			for opt_idx in range(len(options_given)):
				opt_val = options_given[opt_idx]
				try:
					options2return[positionals_names[opt_idx]] = opt_val
					remaining_positionals.pop(0)
				except IndexError:
					pass # undefined positional, already taken care of
		if remaining_positionals:
			_log.error('unconsumed positional options: %s', remaining_positionals)
			options2return['__undefined_options__'] = remaining_positionals

		_log.debug('options found: %s', options2return)
		return options2return

	#--------------------------------------------------------
	def _escape(self, text=None):
		if self.__esc_func is None:
			return text

		assert (text is not None), 'text=None passed to _escape()'
		return self.__esc_func(text)

	#--------------------------------------------------------
	def _escape_dict_like(self, dict_like=None, date_format='%Y %b %d  %H:%M', none_string='', bool_strings=None):
		if bool_strings is None:
			bools = {True: _('true'), False: _('false')}
		else:
			bools = {True: bool_strings[0], False: bool_strings[1]}
		dict2return = {}
		for key in dict(dict_like):
			# FIXME: harden against BYTEA fields
			#if type(self._payload[key]) == ...
			#	dict2return[key] = _('<%s bytes of binary data>') % len(self._payload[key])
			#	continue
			val = dict_like[key]
			if val is None:
				dict2return[key] = none_string
				continue
			if isinstance(val, bool):
				dict2return[key] = bools[val]
				continue
			if isinstance(val, datetime.datetime):
				dict2return[key] = val.strftime(date_format)
				if self.__esc_style in ['latex', 'tex']:
					dict2return[key] = gmTools.tex_escape_string(dict2return[key])
				elif self.__esc_style in ['xetex', 'xelatex']:
					dict2return[key] = gmTools.xetex_escape_string(dict2return[key])
				continue
			try:
				dict2return[key] = str(val, encoding = 'utf8', errors = 'replace')
			except TypeError:
				try:
					dict2return[key] = str(val)
				except (UnicodeDecodeError, TypeError):
					val = '%s' % str(val)
					dict2return[key] = val.decode('utf8', 'replace')
			if self.__esc_style in ['latex', 'tex']:
				dict2return[key] = gmTools.tex_escape_string(dict2return[key])
			elif self.__esc_style in ['xetex', 'xelatex']:
				dict2return[key] = gmTools.xetex_escape_string(dict2return[key])
		return dict2return

#---------------------------------------------------------------------
def test_placeholders_interactively():

	_log.debug('testing for placeholders with pattern: %s', first_pass_placeholder_regex)

	data_source = gmPlaceholderHandler()
	original_line = ''

	while True:
		# get input from user
		line = wx.GetTextFromUser (
			_('Enter some text containing a placeholder:'),
			_('Testing placeholders'),
			centre = True,
			default_value = original_line
		)
		if line.strip() == '':
			break
		original_line = line
		# replace
		placeholders_in_line = regex.findall(first_pass_placeholder_regex, line, regex.IGNORECASE)
		if len(placeholders_in_line) == 0:
			continue
		for placeholder in placeholders_in_line:
			try:
				val = data_source[placeholder]
			except Exception:
				val = _('error with placeholder [%s]') % placeholder
			if val is None:
				val = _('error with placeholder [%s]') % placeholder
			line = line.replace(placeholder, val)
		# show
		msg = _(
			'Input: %s\n'
			'\n'
			'Output:\n'
			'%s'
		) % (
			original_line,
			line
		)
		gmGuiHelpers.gm_show_info (
			title = _('Testing placeholders'),
			info = msg
		)

#=====================================================================
class cMacroPrimitives:
	"""Functions a macro can legally use.

	An instance of this class is passed to the GNUmed scripting
	listener. Hence, all actions a macro can legally take must
	be defined in this class. Thus we achieve some screening for
	security and also thread safety handling.
	"""
	#-----------------------------------------------------------------
	def __init__(self, personality = None):
		if personality is None:
			raise gmExceptions.ConstructorError('must specify personality')
		self.__personality = personality
		self.__attached = 0
		self._get_source_personality = None
		self.__user_done = False
		self.__user_answer = 'no answer yet'
		self.__pat = gmPerson.gmCurrentPatient()

		self.__auth_cookie = str(random.random())
		self.__pat_lock_cookie = str(random.random())
		self.__lock_after_load_cookie = str(random.random())

		_log.info('slave mode personality is [%s]', personality)
	#-----------------------------------------------------------------
	# public API
	#-----------------------------------------------------------------
	def attach(self, personality = None):
		if self.__attached:
			_log.error('attach with [%s] rejected, already serving a client', personality)
			return (0, _('attach rejected, already serving a client'))
		if personality != self.__personality:
			_log.error('rejecting attach to personality [%s], only servicing [%s]' % (personality, self.__personality))
			return (0, _('attach to personality [%s] rejected') % personality)
		self.__attached = 1
		self.__auth_cookie = str(random.random())
		return (1, self.__auth_cookie)
	#-----------------------------------------------------------------
	def detach(self, auth_cookie=None):
		if not self.__attached:
			return 1
		if auth_cookie != self.__auth_cookie:
			_log.error('rejecting detach() with cookie [%s]' % auth_cookie)
			return 0
		self.__attached = 0
		return 1
	#-----------------------------------------------------------------
	def force_detach(self):
		if not self.__attached:
			return 1
		self.__user_done = False
		# FIXME: use self.__sync_cookie for syncing with user interaction
		wx.CallAfter(self._force_detach)
		return 1
	#-----------------------------------------------------------------
	def version(self):
		ver = _cfg.get(option = 'client_version')
		return "GNUmed %s, %s $Revision: 1.51 $" % (ver, self.__class__.__name__)
	#-----------------------------------------------------------------
	def shutdown_gnumed(self, auth_cookie=None, forced=False):
		"""Shuts down this client instance."""
		if not self.__attached:
			return 0
		if auth_cookie != self.__auth_cookie:
			_log.error('non-authenticated shutdown_gnumed()')
			return 0
		wx.CallAfter(self._shutdown_gnumed, forced)
		return 1
	#-----------------------------------------------------------------
	def raise_gnumed(self, auth_cookie = None):
		"""Raise ourselves to the top of the desktop."""
		if not self.__attached:
			return 0
		if auth_cookie != self.__auth_cookie:
			_log.error('non-authenticated raise_gnumed()')
			return 0
		return "cMacroPrimitives.raise_gnumed() not implemented"

	#-----------------------------------------------------------------
	def raise_notebook_plugin(self, auth_cookie = None, a_plugin = None):
		"""Raise a notebook plugin within GNUmed."""
		if not self.__attached:
			return 0

		if auth_cookie != self.__auth_cookie:
			_log.error('non-authenticated raise_notebook_plugin()')
			return 0

		gmDispatcher.send(signal = 'display_widget', name = a_plugin)
		return 1

	#-----------------------------------------------------------------
	def load_patient_from_external_source(self, auth_cookie = None):
		"""Load external patient, perhaps create it.

		Callers must use get_user_answer() to get status information.
		It is unsafe to proceed without knowing the completion state as
		the controlled client may be waiting for user input from a
		patient selection list.
		"""
		if not self.__attached:
			return (0, _('request rejected, you are not attach()ed'))
		if auth_cookie != self.__auth_cookie:
			_log.error('non-authenticated load_patient_from_external_source()')
			return (0, _('rejected load_patient_from_external_source(), not authenticated'))
		if self.__pat.locked:
			_log.error('patient is locked, cannot load from external source')
			return (0, _('current patient is locked'))
		self.__user_done = False
		wx.CallAfter(self._load_patient_from_external_source)
		self.__lock_after_load_cookie = str(random.random())
		return (1, self.__lock_after_load_cookie)
	#-----------------------------------------------------------------
	def lock_loaded_patient(self, auth_cookie = None, lock_after_load_cookie = None):
		if not self.__attached:
			return (0, _('request rejected, you are not attach()ed'))
		if auth_cookie != self.__auth_cookie:
			_log.error('non-authenticated lock_load_patient()')
			return (0, _('rejected lock_load_patient(), not authenticated'))
		# FIXME: ask user what to do about wrong cookie
		if lock_after_load_cookie != self.__lock_after_load_cookie:
			_log.warning('patient lock-after-load request rejected due to wrong cookie [%s]' % lock_after_load_cookie)
			return (0, 'patient lock-after-load request rejected, wrong cookie provided')
		self.__pat.locked = True
		self.__pat_lock_cookie = str(random.random())
		return (1, self.__pat_lock_cookie)

	#-----------------------------------------------------------------
	def lock_into_patient(self, auth_cookie = None, search_params = None):
		if not self.__attached:
			return (0, _('request rejected, you are not attach()ed'))

		if auth_cookie != self.__auth_cookie:
			_log.error('non-authenticated lock_into_patient()')
			return (0, _('rejected lock_into_patient(), not authenticated'))

		if self.__pat.locked:
			_log.error('patient is already locked')
			return (0, _('already locked into a patient'))

		searcher = gmPersonSearch.cPatientSearcher_SQL()
		if type(search_params) == dict:
			#idents = searcher.get_identities(search_dict = search_params)
			raise Exception("must use dto, not search_dict")

		else:
			idents = searcher.get_identities(search_term = search_params)
		if idents is None:
			return (0, _('error searching for patient with [%s]') % search_params)

		if len(idents) == 0:
			return (0, _('no patient found for [%s]') % search_params)

		# FIXME: let user select patient
		if len(idents) > 1:
			return (0, _('several matching patients found for [%s]') % search_params)

		if not gmPatSearchWidgets.set_active_patient(patient = idents[0]):
			return (0, _('cannot activate patient [%s] (%s)') % (str(idents[0]), search_params))

		self.__pat.locked = True
		self.__pat_lock_cookie = str(random.random())
		return (1, self.__pat_lock_cookie)

	#-----------------------------------------------------------------
	def unlock_patient(self, auth_cookie = None, unlock_cookie = None):
		if not self.__attached:
			return (0, _('request rejected, you are not attach()ed'))
		if auth_cookie != self.__auth_cookie:
			_log.error('non-authenticated unlock_patient()')
			return (0, _('rejected unlock_patient, not authenticated'))
		# we ain't locked anyways, so succeed
		if not self.__pat.locked:
			return (1, '')
		# FIXME: ask user what to do about wrong cookie
		if unlock_cookie != self.__pat_lock_cookie:
			_log.warning('patient unlock request rejected due to wrong cookie [%s]' % unlock_cookie)
			return (0, 'patient unlock request rejected, wrong cookie provided')
		self.__pat.locked = False
		return (1, '')
	#-----------------------------------------------------------------
	def assume_staff_identity(self, auth_cookie = None, staff_name = "Dr.Jekyll", staff_creds = None):
		if not self.__attached:
			return 0
		if auth_cookie != self.__auth_cookie:
			_log.error('non-authenticated select_identity()')
			return 0
		return "cMacroPrimitives.assume_staff_identity() not implemented"
	#-----------------------------------------------------------------
	def get_user_answer(self):
		if not self.__user_done:
			return (0, 'still waiting')
		self.__user_done = False
		return (1, self.__user_answer)
	#-----------------------------------------------------------------
	# internal API
	#-----------------------------------------------------------------
	def _force_detach(self):
		msg = _(
			'Someone tries to forcibly break the existing\n'
			'controlling connection. This may or may not\n'
			'have legitimate reasons.\n\n'
			'Do you want to allow breaking the connection ?'
		)
		can_break_conn = gmGuiHelpers.gm_show_question (
			question = msg,
			title = _('forced detach attempt')
		)
		if can_break_conn:
			self.__user_answer = 1
		else:
			self.__user_answer = 0
		self.__user_done = True
		if can_break_conn:
			self.__pat.locked = False
			self.__attached = 0
		return 1
	#-----------------------------------------------------------------
	def _shutdown_gnumed(self, forced=False):
		top_win = wx.GetApp().GetTopWindow()
		if forced:
			top_win.DestroyLater()
		else:
			top_win.Close()
	#-----------------------------------------------------------------
	def _load_patient_from_external_source(self):
		patient = gmPatSearchWidgets.get_person_from_external_sources(search_immediately = True, activate_immediately = True)
		if patient is not None:
			self.__user_answer = 1
		else:
			self.__user_answer = 0
		self.__user_done = True
		return 1
#=====================================================================
# main
#=====================================================================
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')
	from Gnumed.pycommon import gmPG2
	from Gnumed.pycommon import gmLog2
	gmLog2.print_logfile_name()

	#--------------------------------------------------------
	def __test_placeholders():
		handler = gmPlaceholderHandler()
		handler.debug = True

		for placeholder in ['a', 'b']:
			print(handler[placeholder])

		pat = gmPersonSearch.ask_for_patient()
		if pat is None:
			return

		gmPatSearchWidgets.set_active_patient(patient = pat)

		print('DOB (YYYY-MM-DD):', handler['date_of_birth::%Y-%m-%d'])

		ph = 'progress_notes::ap'
		print('%s: %s' % (ph, handler[ph]))
	#--------------------------------------------------------
	def test_new_variant_placeholders():

		tests = [
			# should work:
			'$<lastname>$',
			'$<lastname::::3>$',
			'$<name::%(title)s %(firstnames)s%(preferred)s%(lastnames)s>$',

			# should fail:
			'lastname',
			'$<lastname',
			'$<lastname::',
			'$<lastname::>$',
			'$<lastname::abc>$',
			'$<lastname::abc::>$',
			'$<lastname::abc::3>$',
			'$<lastname::abc::xyz>$',
			'$<lastname::::>$',
			'$<lastname::::xyz>$',

			'$<date_of_birth::%Y-%m-%d>$',
			'$<date_of_birth::%Y-%m-%d::3>$',
			'$<date_of_birth::%Y-%m-%d::>$',

			# should work:
			'$<adr_location::home::35>$',
			'$<gender_mapper::male//female//other::5>$',
			'$<current_meds::==> %(product)s %(preparation)s (%(substance)s) <==\n::50>$',
			'$<allergy_list::%(descriptor)s, >$',
			'$<current_meds_table::latex//>$'

#			'firstname',
#			'title',
#			'date_of_birth',
#			'progress_notes',
#			'soap',
#			'soap_s',
#			'soap_o',
#			'soap_a',
#			'soap_p',

#			'soap',
#			'progress_notes',
#			'date_of_birth'
		]

#		tests = [
#			'$<latest_vaccs_table::latex>$'
#		]

		pat = gmPersonSearch.ask_for_patient()
		if pat is None:
			return

		gmPatSearchWidgets.set_active_patient(patient = pat)

		handler = gmPlaceholderHandler()
		handler.debug = True

		for placeholder in tests:
			print(placeholder, "=>", handler[placeholder])
			print("--------------")
			input()

#		print 'DOB (YYYY-MM-DD):', handler['date_of_birth::%Y-%m-%d']

#		ph = 'progress_notes::ap'
#		print '%s: %s' % (ph, handler[ph])

	#--------------------------------------------------------
	def test_scripting():
		from Gnumed.pycommon import gmScriptingListener
		import xmlrpc.client

		listener = gmScriptingListener.cScriptingListener(macro_executor = cMacroPrimitives(personality='unit test'), port=9999)

		s = xmlrpc.client.ServerProxy('https://localhost:9999')
		print("should fail:", s.attach())
		print("should fail:", s.attach('wrong cookie'))
		print("should work:", s.version())
		print("should fail:", s.raise_gnumed())
		print("should fail:", s.raise_notebook_plugin('test plugin'))
		print("should fail:", s.lock_into_patient('kirk, james'))
		print("should fail:", s.unlock_patient())
		status, conn_auth = s.attach('unit test')
		print("should work:", status, conn_auth)
		print("should work:", s.version())
		print("should work:", s.raise_gnumed(conn_auth))
		status, pat_auth = s.lock_into_patient(conn_auth, 'kirk, james')
		print("should work:", status, pat_auth)
		print("should fail:", s.unlock_patient(conn_auth, 'bogus patient unlock cookie'))
		print("should work", s.unlock_patient(conn_auth, pat_auth))
		data = {'firstname': 'jame', 'lastnames': 'Kirk', 'gender': 'm'}
		status, pat_auth = s.lock_into_patient(conn_auth, data)
		print("should work:", status, pat_auth)
		print("should work", s.unlock_patient(conn_auth, pat_auth))
		print(s.detach('bogus detach cookie'))
		print(s.detach(conn_auth))
		del s

		listener.shutdown()
	#--------------------------------------------------------
	def test_placeholder_regex():

		import re as regex

		tests = [
			' $<lastname>$ ',
			' $<lastname::::3>$ ',

			# should fail:
			'$<date_of_birth::%Y-%m-%d>$',
			'$<date_of_birth::%Y-%m-%d::3>$',
			'$<date_of_birth::%Y-%m-%d::>$',

			'$<adr_location::home::35>$',
			'$<gender_mapper::male//female//other::5>$',
			'$<current_meds::==> %(product)s %(preparation)s (%(substance)s) <==\\n::50>$',
			'$<allergy_list::%(descriptor)s, >$',

			'\\noindent Patient: $<lastname>$, $<firstname>$',
			'$<allergies::%(descriptor)s & %(l10n_type)s & {\\footnotesize %(reaction)s} \tabularnewline \hline >$',
			'$<current_meds::		\item[%(substance)s] {\\footnotesize (%(product)s)} %(preparation)s %(amount)s%(unit)s: %(schedule)s >$'
		]

		tests = [

			'junk	$<lastname::::3>$			junk',
			'junk	$<lastname::abc::3>$		junk',
			'junk	$<lastname::abc>$			junk',
			'junk	$<lastname>$				junk',

			'junk	$<lastname>$   junk   $<firstname>$						junk',
			'junk	$<lastname::abc>$   junk   $<fiststname::abc>$			junk',
			'junk	$<lastname::abc::3>$   junk   $<firstname::abc::3>$		junk',
			'junk	$<lastname::::3>$   junk   $<firstname::::3>$			junk'

		]

		tests = [
#			u'junk   $<<<date_of_birth::%Y %B %d $<inner placeholder::%Y %B %d::20>$::20>>>$   junk',
#			u'junk   $<date_of_birth::%Y %B %d::20>$   $<date_of_birth::%Y %B %d::20>$',
#			u'junk   $<date_of_birth::%Y %B %d::>$   $<date_of_birth::%Y %B %d::20>$   $<<date_of_birth::%Y %B %d::20>>$',
#			u'junk   $<date_of_birth::::20>$',
#			u'junk   $<date_of_birth::::>$',
			'junk $<<<current_meds::%(product)s (%(substance)s): Dispense $<free_text::Dispense how many of %(product)s %(preparation)s (%(substance)s) ?::20>$ (%(preparation)s) \\n::>>>$ junk',
			'junk $<<<current_meds::%(product)s (%(substance)s): Dispense $<free_text::Dispense how many of %(product)s %(preparation)s (%(substance)s) ?::20>$ (%(preparation)s) \\n::250>>>$ junk',
			'junk $<<<current_meds::%(product)s (%(substance)s): Dispense $<free_text::Dispense how many of %(product)s %(preparation)s (%(substance)s) ?::20>$ (%(preparation)s) \\n::3-4>>>$ junk',

			'should fail $<<<current_meds::%(product)s (%(substance)s): Dispense $<free_text::Dispense how many of %(product)s %(preparation)s (%(substance)s) ?::20>$ (%(preparation)s) \\n::->>>$ junk',
			'should fail $<<<current_meds::%(product)s (%(substance)s): Dispense $<free_text::Dispense how many of %(product)s %(preparation)s (%(substance)s) ?::20>$ (%(preparation)s) \\n::3->>>$ junk',
			'should fail $<<<current_meds::%(product)s (%(substance)s): Dispense $<free_text::Dispense how many of %(product)s %(preparation)s (%(substance)s) ?::20>$ (%(preparation)s) \\n::-4>>>$ should fail',
			'should fail $<<<current_meds::%(product)s (%(substance)s): Dispense $<free_text::Dispense how many of %(product)s %(preparation)s (%(substance)s) ?::20>$ (%(preparation)s) \\n::should_fail>>>$ junk',
			'should fail $<<<current_meds::%(product)s (%(substance)s): Dispense $<free_text::Dispense how many of %(product)s %(preparation)s (%(substance)s) ?::20>$ (%(preparation)s) \\n::should_fail->>>$ junk',
			'should fail $<<<current_meds::%(product)s (%(substance)s): Dispense $<free_text::Dispense how many of %(product)s %(preparation)s (%(substance)s) ?::20>$ (%(preparation)s) \\n::-should_fail>>>$ junk',
			'should fail $<<<current_meds::%(product)s (%(substance)s): Dispense $<free_text::Dispense how many of %(product)s %(preparation)s (%(substance)s) ?::20>$ (%(preparation)s) \\n::should_fail-4>>>$ junk',
			'should fail $<<<current_meds::%(product)s (%(substance)s): Dispense $<free_text::Dispense how many of %(product)s %(preparation)s (%(substance)s) ?::20>$ (%(preparation)s) \\n::3-should_fail>>>$ junk',
			'should fail $<<<current_meds::%(product)s (%(substance)s): Dispense $<free_text::Dispense how many of %(product)s %(preparation)s (%(substance)s) ?::20>$ (%(preparation)s) \\n::should_fail-should_fail>>>$ junk',
		]

		tests = [
			'junk $<<<should pass::template::>>>$ junk',
			'junk $<<<should pass::template::10>>>$ junk',
			'junk $<<<should pass::template::10-20>>>$ junk',
			'junk $<<<should pass::template $<<dummy::template 2::10>>$::>>>$ junk',
			'junk $<<<should pass::template $<dummy::template 2::10>$::>>>$ junk',

			'junk $<<<should pass::template::>>>$ junk $<<<should pass 2::template 2::>>>$ junk',
			'junk $<<<should pass::template::>>>$ junk $<<should pass 2::template 2::>>$ junk',
			'junk $<<<should pass::template::>>>$ junk $<should pass 2::template 2::>$ junk',

			'junk $<<<should fail::template $<<<dummy::template 2::10>>>$::>>>$ junk',

			'junk $<<<should fail::template::10->>>$ junk',
			'junk $<<<should fail::template::10->>>$ junk',
			'junk $<<<should fail::template::10->>>$ junk',
			'junk $<<<should fail::template::10->>>$ junk',
			'junk $<first_pass::junk $<<<3rd_pass::template::20>>>$ junk::8-10>$ junk'
		]

		#print "testing placeholder regex:", first_pass_placeholder_regex
		##print "testing placeholder regex:", second_pass_placeholder_regex
		##print "testing placeholder regex:", third_pass_placeholder_regex
		#print ""
		#for t in tests:
		#	print 'line: "%s"' % t
		#	phs = regex.findall(first_pass_placeholder_regex, t, regex.IGNORECASE)
		#	#phs = regex.findall(second_pass_placeholder_regex, t, regex.IGNORECASE)
		#	#phs = regex.findall(third_pass_placeholder_regex, t, regex.IGNORECASE)
		#	print " %s placeholders:" % len(phs)
		#	for p in phs:
		#		print ' => ', p
		#	print " "

		all_tests = {
			first_pass_placeholder_regex: [
				# different lengths/regions
				('junk $<first_level::template::>$ junk', ['$<first_level::template::>$']),
				('junk $<first_level::template::10>$ junk', ['$<first_level::template::10>$']),
				('junk $<first_level::template::10-12>$ junk', ['$<first_level::template::10-12>$']),

				# inside is other-level:
				('junk $<first_level::$<<insert::insert_template::0>>$::10-12>$ junk', ['$<first_level::$<<insert::insert_template::0>>$::10-12>$']),
				('junk $<first_level::$<<<insert::insert_template::0>>>$::10-12>$ junk', ['$<first_level::$<<<insert::insert_template::0>>>$::10-12>$']),

				# outside is other-level:
				('junk $<<second_level::$<insert::insert_template::0>$::10-12>>$ junk', ['$<insert::insert_template::0>$']),
				('junk $<<<third_level::$<insert::insert_template::0>$::10-12>>>$ junk', ['$<insert::insert_template::0>$']),

				# other level on same line
				('junk $<first_level 1::template 1::>$ junk $<<second_level 2::template 2::>>$ junk', ['$<first_level 1::template 1::>$']),
				('junk $<first_level 1::template 1::>$ junk $<<<third_level 2::template 2::>>>$ junk', ['$<first_level 1::template 1::>$']),

				# this should produce 2 matches
				('junk $<first_level 1::template 1::>$ junk $<first_level 2::template 2::>$ junk', ['$<first_level 1::template 1::>$', '$<first_level 2::template 2::>$']),

				# this will produce a mismatch, due to illegal nesting of same-level placeholders
				('returns illegal match: junk $<first_level::$<insert::insert_template::0>$::10-12>$ junk', ['$<first_level::$<insert::insert_template::0>$::10-12>$']),
			],
			second_pass_placeholder_regex: [
				# different lengths/regions
				('junk $<<second_level::template::>>$ junk', ['$<<second_level::template::>>$']),
				('junk $<<second_level::template::10>>$ junk', ['$<<second_level::template::10>>$']),
				('junk $<<second_level::template::10-12>>$ junk', ['$<<second_level::template::10-12>>$']),

				# inside is other-level:
				('junk $<<second_level::$<insert::insert_template::0>$::10-12>>$ junk', ['$<<second_level::$<insert::insert_template::0>$::10-12>>$']),
				('junk $<<second_level::$<<<insert::insert_template::0>>>$::10-12>>$ junk', ['$<<second_level::$<<<insert::insert_template::0>>>$::10-12>>$']),

				# outside is other-level:
				('junk $<first_level::$<<insert::insert_template::0>>$::10-12>$ junk', ['$<<insert::insert_template::0>>$']),
				('junk $<<<third_level::$<<insert::insert_template::0>>$::10-12>>>$ junk', ['$<<insert::insert_template::0>>$']),

				# other level on same line
				('junk $<first_level 1::template 1::>$ junk $<<second_level 2::template 2::>>$ junk', ['$<<second_level 2::template 2::>>$']),
				('junk $<<second_level 1::template 1::>>$ junk $<<<third_level 2::template 2::>>>$ junk', ['$<<second_level 1::template 1::>>$']),

				# this should produce 2 matches
				('junk $<<second_level 1::template 1::>>$ junk $<<second_level 2::template 2::>>$ junk', ['$<<second_level 1::template 1::>>$', '$<<second_level 2::template 2::>>$']),

				# this will produce a mismatch, due to illegal nesting of same-level placeholders
				('returns illegal match: junk $<<second_level::$<<insert::insert_template::0>>$::10-12>>$ junk', ['$<<second_level::$<<insert::insert_template::0>>$::10-12>>$']),

			],
			third_pass_placeholder_regex: [
				# different lengths/regions
				('junk $<<<third_level::template::>>>$ junk', ['$<<<third_level::template::>>>$']),
				('junk $<<<third_level::template::10>>>$ junk', ['$<<<third_level::template::10>>>$']),
				('junk $<<<third_level::template::10-12>>>$ junk', ['$<<<third_level::template::10-12>>>$']),

				# inside is other-level:
				('junk $<<<third_level::$<<insert::insert_template::0>>$::10-12>>>$ junk', ['$<<<third_level::$<<insert::insert_template::0>>$::10-12>>>$']),
				('junk $<<<third_level::$<insert::insert_template::0>$::10-12>>>$ junk', ['$<<<third_level::$<insert::insert_template::0>$::10-12>>>$']),

				# outside is other-level:
				('junk $<<second_level::$<<<insert::insert_template::0>>>$::10-12>>$ junk', ['$<<<insert::insert_template::0>>>$']),
				('junk $<first_level::$<<<insert::insert_template::0>>>$::10-12>$ junk', ['$<<<insert::insert_template::0>>>$']),

				# other level on same line
				('junk $<first_level 1::template 1::>$ junk $<<<third_level 2::template 2::>>>$ junk', ['$<<<third_level 2::template 2::>>>$']),
				('junk $<<second_level 1::template 1::>>$ junk $<<<third_level 2::template 2::>>>$ junk', ['$<<<third_level 2::template 2::>>>$']),

				# this will produce a mismatch, due to illegal nesting of same-level placeholders
				('returns illegal match: junk $<<<third_level::$<<<insert::insert_template::0>>>$::10-12>>>$ junk', ['$<<<third_level::$<<<insert::insert_template::0>>>$::10-12>>>$']),
			]
		}

		for pattern in [first_pass_placeholder_regex, second_pass_placeholder_regex, third_pass_placeholder_regex]:
			print("")
			print("-----------------------------")
			print("regex:", pattern)
			tests = all_tests[pattern]
			for t in tests:
				line, expected_results = t
				phs = regex.findall(pattern, line, regex.IGNORECASE)
				if len(phs) > 0:
					if phs == expected_results:
						continue

				print("")
				print("failed")
				print("line:", line)

				if len(phs) == 0:
					print("no match")
					continue

				if len(phs) > 1:
					print("several matches")
					for r in expected_results:
						print("expected:", r)
					for p in phs:
						print("found:", p)
					continue

				print("unexpected match")
				print("expected:", expected_results)
				print("found:   ", phs)

	#--------------------------------------------------------
	def test_placeholder():

		phs = [
			#u'emr_journal::soapu //%(clin_when)s  %(modified_by)s  %(soap_cat)s  %(narrative)s//1000 days::',
			#u'free_text::placeholder test//preset::9999',
			#u'soap_for_encounters:://::9999',
			#u'soap_p',
			#u'encounter_list::%(started)s: %(assessment_of_encounter)s::30',
			#u'patient_comm::homephone::1234',
			#u'$<patient_address::work::1234>$',
			#u'adr_region::home::1234',
			#u'adr_country::fehlt::1234',
			#u'adr_subunit::fehlt::1234',
			#u'adr_suburb::fehlt-auch::1234',
			#u'external_id::Starfleet Serial Number//Star Fleet Central Staff Office::1234',
			#u'primary_praxis_provider',
			#u'current_provider::::3-5',
			#u'current_provider_external_id::Starfleet Serial Number//Star Fleet Central Staff Office::1234',
			#u'current_provider_external_id::LANR//LÄK::1234'
			#u'$<current_provider_external_id::KV-LANR//KV::1234>$'
			#u'primary_praxis_provider_external_id::LANR//LÄK::1234'
			#u'form_name_long::::1234',
			#u'form_name_long::::5',
			#u'form_name_long::::',
			#u'form_version::::5',
			#u'$<current_meds::\item %(product)s %(preparation)s (%(substance)s) from %(started)s for %(duration)s as %(schedule)s until %(discontinued)s\\n::250>$',
			#u'$<vaccination_history::%(date_given)s: %(vaccine)s [%(batch_no)s] %(l10n_indications)s::250>$',
			#u'$<date_of_birth::%Y %B %d::20>$',
			#u'$<date_of_birth::%Y %B %d::>$',
			#u'$<date_of_birth::::20>$',
			#u'$<date_of_birth::::>$',
			#u'$<patient_tags::Tag "%(l10n_description)s": %(comment)s//\\n- ::250>$',
			#u'$<PHX::%(description)s\n  side: %(laterality)s, active: %(is_active)s, relevant: %(clinically_relevant)s, caused death: %(is_cause_of_death)s//\n//%Y %B %d//latex::250>$',
			#u'$<patient_photo::\includegraphics[width=60mm]{%s}//image/png//.png::250>$',
			#u'$<data_snippet::binary_test_snippet//path=<%s>//image/png//.png::250>$',
			#u'$<data_snippet::autograph-LMcC//path=<%s>//image/jpg//.jpg::250>$',
			#u'$<current_meds::%s ($<lastname::::50>$)//select::>$',
			#u'$<current_meds::%s//select::>$',
			#u'$<soap_by_issue::soapu //%Y %b %d//%(narrative)s::1000>$',
			#u'$<soap_by_episode::soapu //%Y %b %d//%(narrative)s::1000>$',
			#u'$<documents::select//description//document %(clin_when)s: %(l10n_type)s// file: %(fullpath)s (<some path>/%(name)s)//~/gnumed/export/::>$',
			#u'$<soap::soapu //%s::9999>$',
			#u'$<soap::soapu //%(soap_cat)s: %(date)s | %(provider)s | %(narrative)s::9999>$'
			#u'$<test_results:://%c::>$'
			#u'$<test_results::%(unified_abbrev)s: %(unified_val)s %(val_unit)s//%c::>$'
			#'$<most_recent_test_results::tmpl=%(unified_name)s & %(unified_val)s%(val_unit)s & [%(unified_target_min)s--%(unified_target_max)s] %(unified_target_range)s & %(clin_when)s \\tabularnewline::>$'		#<dfmt=...>//<tmpl=...>//<sep=...>
			#u'$<reminders:://::>$'
			#u'$<current_meds_for_rx::%(product)s (%(contains)s): dispense %(amount2dispense)s ::>$'
			#u'$<praxis::%(branch)s (%(praxis)s)::>$'
			#u'$<praxis_address::::120>$'
			#u'$<praxis_id::::120>$'
			#u'$<gen_adr_street::Street = %s//Wählen Sie die Empfängeradresse !::120>$', u'$<gen_adr_location::Ort = %s::120>$', u'$<gen_adr_country::::120>$'

			#u'$<receiver_name::%s::120>$',
			#u'$<receiver_street::%s//a::120>$',
			#u'$<receiver_number:: %s//a::120>$',
			#u'$<receiver_subunit:: %s::120>$',
			#u'$<receiver_postcode::%s//b::120>$',
			#u'$<receiver_location:: %s::120>$',
			#u'$<receiver_country::, %s::120>$',
			#u'$<external_care::%(issue)s: %(provider)s of %(unit)s@%(organization)s (%(comment)s)::1024>$',
			#u'$<url_escape::hello world ü::>$',
			#u'$<substance_abuse::%(substance)s (%(use_type)s) last=%(last_checked_when)s stop=%(discontinued)s // %(notes)s::>$',
			#u'bill_adr_region::region %s::1234',
			#u'bill_adr_country::%s::1234',
			#u'bill_adr_subunit::subunit: %s::1234',
			#u'bill_adr_suburb::-> %s::1234',
			#u'bill_adr_street::::1234',
			#u'bill_adr_number::%s::1234',
			#u'$<diagnoses::\listitem %s::>$'
			#u'$<patient_mcf::fmt=txt//card=%s::>$',
			#u'$<patient_mcf::fmt=mcf//mcf=%s::>$',
			#u'$<patient_mcf::fmt=qr//png=%s::>$'
			#u'$<praxis_scan2pay::fmt=txt::>$',
			#u'$<praxis_scan2pay::fmt=qr::>$'
			#u'$<bill_scan2pay::fmt=txt::>$',
			#u'$<bill_scan2pay::fmt=qr::>$',
			#'$<yes_no::msg=do you want to select yes or no or something else ?  Look at the title//yes=it was yes//no=oh no!::>$'
			#'$<data_snippet::autograph-ncq//path=<%s>//image/jpg//.jpg::250>$',
			'$<current_meds_AMTS::::>$'
		]

#		from Gnumed.pycommon import gmPG2
#		from Gnumed.pycommon import gmConnectionPool
#		l, creds = gmPG2.request_login_params()
#		pool = gmConnectionPool.gmConnectionPool()
#		pool.credentials = creds

		handler = gmPlaceholderHandler()
		handler.debug = True

		gmStaff.set_current_provider_to_logged_on_user()
		gmPraxisWidgets.set_active_praxis_branch(no_parent = True)
		pat = gmPersonSearch.ask_for_patient()
		if pat is None:
			return
		gmPatSearchWidgets.set_active_patient(patient = pat)

		#handler.set_placeholder('form_name_long', 'ein Testformular')
		for ph in phs:
			print(ph)
			print(" result:")
			print('  %s' % handler[ph])
		#handler.unset_placeholder('form_name_long')

	#--------------------------------------------------------
	def test():
		pat = gmPersonSearch.ask_for_patient()
		if pat is None:
			sys.exit()
		gmPerson.set_active_patient(patient = pat)
		from Gnumed.wxpython import gmSubstanceIntakeWidgets
		gmSubstanceIntakeWidgets.manage_substance_intakes()

	#--------------------------------------------------------
	def test_show_phs():
		show_placeholders()

	#--------------------------------------------------------
	def test_parse_ph_options():
		handler = gmPlaceholderHandler()
		option_str = '//select//pos1//opt1=one//opt2=2//opt3=drei//positional_further_down//fmt=qr//%s//tmpl=__%s__//switch=with=equal_sig//empty_kwd='
		switches = {'select': False, 'verbose': False, 'switch=with=equal_sign': None}
		kwds = {'opt1': 1, 'opt2': 'two', 'opt4': 'vier', 'fmt': 'qr', 'tmpl': '--%s--', 'switch': 'what ??', 'empty_kwd': ''}
		pos = {'empty': None, 'firstpos': 'egal', 'farther_away': None, 'tmpl':None, 'one too many': 99999}

		opts = handler._parse_ph_options (
			options_data = option_str
			#, switch_defaults = switches
			#, kwd_defaults = kwds
			#, pos_defaults= None
		)
		print(option_str)
		print('no definitions:')
		for key in opts:
			print(' ', key, '-->', opts[key])

		input()
		opts = handler._parse_ph_options (
			options_data = option_str
			, switch_defaults = switches
			#, kwd_defaults = kwds
			#, pos_defaults= None
		)
		print()
		print(option_str)
		print('switches defined:')
		for key in opts:
			print(' ', key, '-->', opts[key])

		input()
		opts = handler._parse_ph_options (
			options_data = option_str
			, switch_defaults = switches
			, kwd_defaults = kwds
			#, pos_defaults= None
		)
		print()
		print(option_str)
		print('switches and kwds defined:')
		for key in opts:
			print(' ', key, '-->', opts[key])

		input()
		opts = handler._parse_ph_options (
			options_data = option_str
			, switch_defaults = switches
			, kwd_defaults = kwds
			, pos_defaults = pos
		)
		print()
		print(option_str)
		print('switches and kwds and positionals defined:')
		for key in opts:
			print(' ', key, '-->', opts[key])

		input()
		opts = handler._parse_ph_options (
			options_data = option_str
			#, switch_defaults = switches
			, kwd_defaults = kwds
			#, pos_defaults= None
		)
		print()
		print(option_str)
		print('kwds defined:')
		for key in opts:
			print(' ', key, '-->', opts[key])

#		one, two, four, legacy = handler._parse_ph_options (
#			option_defs = {'__legacy_options__': None, 'opt1': 1, 'opt2': 'two', 'opt4': 'vier'},
#			options_string = 'pos1//opt1=one//opt2=2//opt3=drei//legacy_lives_forever',
#			ignore_positional_options = False
#		)
#		print(one, two, four, legacy)

	#--------------------------------------------------------
	gmPG2.request_login_params(setup_pool = True, force_tui = True)

	#test_parse_ph_options()
	#sys.exit()

	app = wx.App()

	test_placeholder()
	#test_new_variant_placeholders()
	#test_scripting()
	#test_placeholder_regex()
	#test()
	#test_placeholder()
	#test_show_phs()
