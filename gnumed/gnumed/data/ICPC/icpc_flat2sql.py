# -*- coding: utf8 -*-

import sys
import io

fname = sys.argv[1]

#================================================================================
SQL_SCRIPT_START = u"""-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;


-- --------------------------------------------------------------
-- translations

-- chapters
select i18n.upd_tx('de', 'General and Unspecified', 'Allgmein und unspezifisch');
select i18n.upd_tx('de', 'Blood, Blood forming organs, Immune mechanism', 'Blut, blutbildende Organe, Immunsystem');
select i18n.upd_tx('de', 'Digestive', 'Darm: Verdauungssystem');
select i18n.upd_tx('de', 'Eye ("Focal")', 'Fokus: Auge');
select i18n.upd_tx('de', 'Ear ("Hearing")', 'Hören: Ohr');
select i18n.upd_tx('de', 'Cardivascular', 'Kreislauf');
select i18n.upd_tx('de', 'Musculoskeletal ("Locomotion")', 'Laufen: Bewegungsapparat');
select i18n.upd_tx('de', 'Neurological', 'Neurologisch');
select i18n.upd_tx('de', 'Psychological', 'Psychologisch');
select i18n.upd_tx('de', 'Respiratory', 'Respiratorisch: Atmungsorgane');
select i18n.upd_tx('de', 'Skin', 'Skin: Haut');
select i18n.upd_tx('de', 'Endocrine/Metabolic and Nutritional ("Thyroid")', 'Thyroidea: Endokrin, metabolisch, Ernährung');
select i18n.upd_tx('de', 'Urological', 'Urologisch');
select i18n.upd_tx('de', 'Pregnancy, Childbearing, Family planning ("Women")', 'Weiblich: Schwangerschaft, Geburt, Familienplanung');
select i18n.upd_tx('de', 'Female genital ("X-chromosome")', 'X-Chromosom: Weibliches Genitale, Brust');
select i18n.upd_tx('de', 'Male genital ("Y-chromosome")', 'Y-Chromosom: Männliches Genitale, Brust');
select i18n.upd_tx('de', 'Social problems', 'SoZiale Probleme');

-- components
select i18n.upd_tx('de', 'Symptoms, complaints', 'Symptome, Beschwerden');
select i18n.upd_tx('de', 'Diagnostic screening, prevention', 'Diagnostik, Screening, Prävention');
select i18n.upd_tx('de', 'Treatment, procedures, medication', 'Behandlung, Prozeduren, Medikation');
select i18n.upd_tx('de', 'Test results', 'Testresultate');
select i18n.upd_tx('de', 'Administrative', 'Administrativ');
select i18n.upd_tx('de', 'Other (referral etc)', 'Anderes');
select i18n.upd_tx('de', 'Diagnosis, disease', 'Diagnosen, Krankheiten');

-- --------------------------------------------------------------
\\unset ON_ERROR_STOP
drop table staging.icpc cascade;
\set ON_ERROR_STOP 1

create table staging.icpc (
	icpc text,
	component integer,
	chapter text,
	term text,
	icd10 text,
	incl text,
	excl text,
	crit text,
	notes text,
	see_also text
);

-- --------------------------------------------------------------
"""

record_separator = '*|||*'

SQL_SCRIPT_END = u"""
-- --------------------------------------------------------------
-- create data source

delete from ref.data_source
where
	name_short = 'ICPC'
		and
	version = '2e-3.0-GM-2004'
		and
	lang = 'de';

insert into ref.data_source (
	name_long,
	name_short,
	version,
	description,
	source,
	lang
) values (
	'International Classification of Primary Care',
	'ICPC',
	'2e-3.0-GM-2004',
	'The ICPC2 data which comes with GNUmed is intended for NON-COMMERCIAL USE ONLY !

Use in a commercial way requires getting a license from WONCA and translation teams.

--------------------------------------------------------------------------------------
The German translation has been typed in based on data from
the CONTENT Project, University of Heidelberg.

	http://www.content-info.org

--------------------------------------------------------------------------------------
Copyright notices from the WONCA pages:

(http://www.kith.no/templates/kith_WebPage____1110.aspx)

Policy on copyright, licensing and translations


The copyright of ICPC, both in hard copy and in electronic form, is owned by Wonca.  

The non-commercial user is free to use ICPC-2e.

If ICPC-2e is to be used for commercial purposes or in national/local coding systems, it will be necessary to negotiate with
Wonca about user fees. In that case, please contact the CEO of Wonca (ceo@wonca.com.sg).

In the following the copyright and licensing policy as well as the translation policy related to the electronic version
(ICPC-2e) is stated:

Aims OF THE POLICY

 1. To allow the Wonca Classification Committee to promote, distribute, and support ICPC-2, and further develop it as the best
    classification for primary care.
 2. To maintain international comparability of versions of ICPC-2.
 3. To obtain feedback and maintain a clearing-house of international experiences with ICPC-2.
 4. To achieve recognition of Wonca''s initiative and expertise in classification.
 5. To promote understanding of appropriate links between ICPC-2 and other classification and coding systems, particularly
    ICD-10.
 6. To encourage use of ICPC-2 rather than inhibit it with restrictions.
 7. To obtain financial support to enable achievement of these aims and allow the work of the Wonca Classification Committee
    to continue and expand.

copyright and licensing Policy

 1. The electronic version of ICPC-2 should be made available in as many countries as possible.
 2. Versions involving additions, translations, or alterations should be made with input from and agreement of the Wonca
    Classification Committee if they are to be regarded as official Wonca versions.
 3. Wonca should licence appropriate organizations to promote and distribute electronic versions of ICPC-2 in countries,
    regions, and language groups.
 4. Licence fees may be charged through these organizations to the end users and collected by the distributors for Wonca. The
    fees will be set by negotiation and may be waived when there are advantages to Wonca by so doing, such as when use is for
    research or development.

Translation policy

Wonca is an international organization and wishes to promote versions of ICPC in languages other than English, which is the
working language of the Classification Committee.  ICPC (the first version) has already been translated into 19 languages, and
has been published as a book in some of these.  There are already several translations of ICPC-2 being undertaken.  The
committee encourages anyone wishing to promote, assist with, or undertake translations of ICPC-2 to contact them to arrange
cooperative work.

The Wonca policy on ICPC-2  translations is:

 1. Wonca encourages versions in languages other than English.
 2. These must include the whole book, not just the rubrics.
 3. There must be no changes to the rubrics. Any extensions must be clearly indicated as such, and approved by the Wonca
    Classification Committee (WICC) prior to publication.
 4. Translations must be prepared by named translators working in cooperation with the Wonca Classification Committee and to
    the standards that it sets, particularly in relation to the extent of back translation for checking which may be required.
 5. While Wonca will retain the copyright it will usually grant without fee the rights to translating organizations to retain
    royalties on their versions. This will require a formal agreement between Wonca and the organization or publisher
    concerned.

Last updated: December 18, 2006


Again, all the ICPC2 data is provided for NON-COMMERCIAL USE ONLY !
',
	'some data downloaded from http://www.kith.no/templates/kith_WebPage____1110.aspx, other parts typed in manually from other sources',
	'de'
);


-- ----------------------------------------------------
-- insert data
delete from ref.icpc
where
	fk_data_source = (
		select pk from ref.data_source where name_short = 'ICPC' and version = '2e-3.0-GM-2004' and lang = 'de'
);


insert into ref.icpc (
	code,
	term,
	comment,
	short_description,
	icd10,
	criteria,
	inclusions,
	exclusions,
	see_also,
	fk_component,
	fk_chapter,
	fk_data_source
) select
	icpc,
	term,
	notes,
	NULL,
	string_to_array(icd10, ' %s '),
	crit,
	incl,
	string_to_array(excl, ' %s '),
	string_to_array(see_also, ' %s '),
	component::smallint,
	chapter,
	(select pk from ref.data_source where name_short = 'ICPC' and version = '2e-3.0-GM-2004' and lang = 'de')
  from
	staging.icpc
;


-- delete staging data
delete from staging.icpc;
drop table staging.icpc cascade;

-- ----------------------------------------------------
""" % (record_separator, record_separator, record_separator)

record_start = u'/stammdatei/body/ICPC_liste/ICPC_stammsatz/ICPC_code/@V='

line_starts = {
	u'/stammdatei/body/ICPC_liste/ICPC_stammsatz/ICPC_code/@V=': u'icpc',
	u'/stammdatei/body/ICPC_liste/ICPC_stammsatz/komponentennummer/@V=': u'component',
	u'/stammdatei/body/ICPC_liste/ICPC_stammsatz/kapitel/@V=': u'chapter',
	u'/stammdatei/body/ICPC_liste/ICPC_stammsatz/bezeichnung/@V=': u'term',
	u'/stammdatei/body/ICPC_liste/ICPC_stammsatz/ICD_liste/ICD_code/@V=': u'icd10',
	u'/stammdatei/body/ICPC_liste/ICPC_stammsatz/einschlussliste/einschlusstext/@V=': u'incl',
	u'/stammdatei/body/ICPC_liste/ICPC_stammsatz/ausschlussliste/ausschluss/ausschlusstext/@V=': u'excl',
	u'/stammdatei/body/ICPC_liste/ICPC_stammsatz/ausschlussliste/ausschluss/ICPC_code/@V=': u'excl',
	u'/stammdatei/body/ICPC_liste/ICPC_stammsatz/kriterien/@V=': u'crit',
	u'/stammdatei/body/ICPC_liste/ICPC_stammsatz/bemerkungen/@V=': u'notes',
	u'/stammdatei/body/ICPC_liste/ICPC_stammsatz/verweisliste/verweis/verweistext/@V=': u'see_also',
	u'/stammdatei/body/ICPC_liste/ICPC_stammsatz/verweisliste/verweis/ICPC_code/@V=': u'see_also'
}

line_starts_to_append = [
	u'/stammdatei/body/ICPC_liste/ICPC_stammsatz/ausschlussliste/ausschluss/ICPC_code/@V=',
	u'/stammdatei/body/ICPC_liste/ICPC_stammsatz/verweisliste/verweis/ICPC_code/@V='
]

SQL_INSERT = u'INSERT INTO staging.icpc (icpc, component, chapter, term, icd10, incl, excl, crit, notes, see_also) VALUES (%s);\n'
SQL_INSERT = SQL_INSERT % (u"%(icpc)s, %(component)s::smallint, %(chapter)s, %(term)s, %(icd10)s, %(incl)s, %(excl)s, %(crit)s, %(notes)s, %(see_also)s")

#================================================================================
NULL = u'NULL'

def init_record():
	return {
		u'icpc': NULL,
		u'component': NULL,
		u'chapter': NULL,
		u'term': NULL,
		u'icd10': NULL,
		u'incl': NULL,
		u'excl': NULL,
		u'crit': NULL,
		u'notes': NULL,
		u'see_also': NULL
	}
#================================================================================
outfile = io.open('v15-ref-icpc2_de-data.sql', mode = 'wt', encoding = 'utf8')
outfile.write(SQL_SCRIPT_START)

infile = io.open(fname, mode = 'rt', encoding = 'utf8')

current_record = None
for line in infile:
	known_line = False
	line = line.strip(u'\n')

	if line.startswith(record_start):
		if current_record is not None:
			outfile.write (SQL_INSERT % current_record)
		current_record = init_record()

	for line_start, sql_field in line_starts.items():
		if line.startswith(line_start):
			known_line = True
			val = line[len(line_start):].replace(u"'", u"''")
			if current_record[sql_field] == NULL:
				current_record[sql_field] = u"'%s'" % val
			else:
				old_val = current_record[sql_field][1:-1]
				if line_start in line_starts_to_append:
					current_record[sql_field] = u"'%s; %s'" % (old_val, val)
				else:
					current_record[sql_field] = u"'%s %s %s'" % (old_val, record_separator, val)
			break

	if known_line:
		continue

	print "unknown line start:", line

infile.close()

outfile.write(SQL_INSERT % current_record)
outfile.write(SQL_SCRIPT_END)
outfile.close()

#================================================================================
