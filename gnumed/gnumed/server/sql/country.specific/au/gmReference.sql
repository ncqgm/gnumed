-- Project: GnuMed - service "Reference" -- Australian specific stuff
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/au/gmReference.sql,v $
-- $Revision: 1.13 $
-- license: GPL
-- author: Ian Haywood

-- This file populates the tables in the reference service with Australian-specific content.
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================

insert into form_types (name) values ('workplace sick certificate');
insert into form_types (name) values ('vaccination report');
-- a list of persons (usually children) vaccinated, to a central
-- government registry
insert into form_types (name) values ('referral');
insert into form_types (name) values ('surveillance');
-- a report of disease case to a public health authority
insert into form_types (name) values ('prescription');
insert into form_types (name) values ('invoice');
insert into form_types (name) values ('bulk invoice');
-- a list of services performed to a whole group of patients,
-- to an insurer.
insert into form_types (name) values ('request');
-- pathology/radiology/physio/etc.
insert into form_types (name) values ('reminder');
-- a reminder letter to patient, asking them to make an appointment

insert into form_defs (fk_type, country, name_short, name_long, revision, engine, is_user, template) values (5,
	'AU',
	'Standard Referral',
	'Standard specialist referral letter for AU',
	1,
	'L',
	false,
'\\documentclass{letter}
\\address{ @"%(title)s %(first)s %(last)s" % user.get_names ()@ \\\\ 
@"%(number)s %(street)s" % user[''addresses''][''work'']@ \\\\
@"%(city)s %(postcode)s" % user[''addresses''][''work'']@ \\\\}
\\signature{ @"%(title)s %(first)s %(last)s" % user.get_names ()@}
\\begin{document}
\\begin{letter}{@"%(title)s %(first)s %(last)s" % addressee.get_names ()@ \\\\ 
@"%(number)s %(street)s" % address@ \\\\
@"%(urb)s %(postcode)s" % address@ \\\\} }

\\opening{Dear @"%(title)s %(first)s %(last)s" % addressee.get_names ()@ }

\\textbf{Re:} @"%(first)s %(last)s" % patient.get_names ()@, 
@"%(number)s %(street)s, %(city)s %(postcode)s" % patient[''addresses''][''home'']@, 
DOB: @patient.getDOB ().Format (''%x'')@

@text@

\\ifnum@incl_meds@>0
\\textbf{Medications List}

\\begin{tabular}{lll}
@[[med[''name''], med[''form''], med[''direction'']] for med in clinical.getMedicationsList ()]@
\\end{tabular}
\\fi

\\ifnum@flags[''incl_phx'']@>0
\\textbf{Disease List}

\\begin{tabular}{ll}
@[[phx[''diagnosis''], phx[''started'']] for phx in clinical.getPastHistory ()]@
\\end{tabular}
\\fi

\\closing{Yours sincerely,}

\\end{letter}
\\end{document}');

insert into form_fields (fk_form, long_name, template_placeholder, help, fk_type, param, display_order ) values
( 1, 'Addressee', 'addressee', 
  'Person the referral is sent to', 
  6,
  NULL, 1);
insert into form_fields (fk_form, long_name, template_placeholder, help, fk_type, param, display_order ) values
( 1, 'Address', 'address', 
  'Address to mail to', 
  7,
  NULL, 2);
insert into form_fields (fk_form, long_name, template_placeholder, help, fk_type, param, display_order ) values
( 1, 'Text', 'text', 
  'Text of referral', 
  4,
  NULL, 3);
insert into form_fields (fk_form, long_name, template_placeholder, help, fk_type, param, display_order ) values
( 1, 'Include medications', 'incl_meds', 
  '', 
  3,
  NULL, 4);
insert into form_fields (fk_form, long_name, template_placeholder, help, fk_type, param, display_order ) values
( 1, 'Include past history', 'incl_phx', 
  '', 
  3,
  NULL, 5);




insert into form_defs (fk_type, country, name_short, name_long, revision, engine, is_user, template) values (
	7,
	'AU', 
	'PBS Script',
	'Prescription using the standard form of the Pharmaceutical Benefits Scheme',
	1,
	'L',
	false,
'\\documentclass{a4form}
\\usepackage{multicol}
% this is a template of a *community* PBS script form
% (hospital scripts are completely different and must be handwritten [sob])

\\begin{document}
\\begin{page}
\\text{25}{25}{80}{@user[''ext_ids'']["Prescriber No."]@}
\\text{130}{25}{80}{@user[''ext_ids'']["Prescriber No."]@}

\\text{35}{33}{80}{@(patient[''ext_ids''].has_key ("Repat No.") and patient[''ext_ids''][''Repat No.'']) or patient[''ext_ids'']["Medicare No."]@}
\\text{140}{33}{80}{@(patient.[[''ext_ids''].has_key (''Repat No.''] and patient[''ext_ids'']["Repat No."]) or patient[''ext_ids'']["Medicare No."]@}
% use the Department of Veteran''s affairs number if available: these patients get extra benefits

\\text{24}{57}{80}{@"%(first)s %(last)s" % patient.get_names ()@}
\\text{129}{57}{80}{@"(first)s %(last)s" % patient.get_names ()@}

\\text{15}{60}{80}{@"%(number)s %(street)s, %(city)s %(postcode)s" % patient[''addresses''][''home'']@}
\\text{120}{60}{80}{@"%(number)s %(street)s, %(city)s %(postcode)s" % patient[''addresses''][''home'']@}

\\text{9}{72}{50}{\\today}
\\text{114}{72}{50}{\\today}

\\ifnum@patient[''ext_id''s].has_key ("Repat No.")@>0
\\text{27}{77}{10}{X} % mark as RPBS script
\\text{132}{77}{10}{X}
\\else
\\text{7}{77}{10}{X} % ordinary PBS
\\text{112}{77}{10}{X}
\\fi

\\ifnum@brand@>0
\\text{43}{74.5}{7}{X}
\\text{148}{74.5}{7}{X}
\\fi

\\text{22.5}{84}{82.5}{
% TODO: drugs business objects yet to be written
\\vspace{1cm}
\\hspace{1cm} @"%(name)s %(form)s %(direction)s " % drug_list@
}

\\text{127.5}{84}{82.5}{
% TODO: drugs business objects yet to be written
\\vspace{1cm}
\\hspace{1cm} @"%(name)s %(form)s %(direction)s" % drug_list@
}
\\end{page}
\\end{document}');

insert into form_fields (fk_form, long_name, template_placeholder, help, fk_type, param, display_order ) values
( 2, 'Items', 'drug_list', 
  'Drugs to be prescribed', 
  8,
  NULL, 1);
insert into form_fields (fk_form, long_name, template_placeholder, help, fk_type, param, display_order ) values
( 2, 'Brand only', 'brand', 
  'Brand-subsitution by pharmacist forbidden', 
  3,
  NULL, 2);


insert into form_defs (fk_type, country, name_short, name_long, revision, engine, is_user, template) values (
	(select pk from form_types where name='request'),
	'AU',
	'Basic request',
	'A proof-of-concept basic request form',
	1,
	'L',
	false,
'\\documentclass{a4form}
\\usepackage{multicol}

\\begin{document}
\\begin{page}
\\text{20}{12}{70}{} % to address

\\lineh{20}{40}{170} % horizontal separators
\\lineh{20}{50}{110}
\\lineh{20}{80}{170}
\\lineh{20}{135}{170}
\\lineh{20}{220}{170}
\\lineh{20}{255}{170}

\\linev{20}{40}{215} % sidelines
\\linev{190}{40}{215}

\\linev{130}{40}{95} % broken vertical separator
\\linev{130}{220}{35}

\\lineh{130}{107}{60} % smaller separators
\\linev{57}{40}{10}
\\linev{90}{40}{10}

\\text{22}{45}{20}{Billing}
\\text{59}{45}{15}{Our ref:}
\\text{92}{45}{20}{Your ref:}
\\text{133}{45}{55}{
\\textbf{Requesting Practitioner}\\
\\
@''%(title)s %(firstnames)s %(lastnames)s'' % user.get_names ()@\\\\
@''%(number)s %(street)s'' % user[''addresses''][``work'']\\\\
@''%(city)s %(postcode)s'' % user[''addresses''][``work'']\\\\
@user[''comms''].has_key (''fax'') and ''FAX: %s\\\\\\\\'' % user[''comms''][''fax'']@
@user[''comms''].has_key (''telephone'') and ''PHONE: %s\\\\\\\\'' % user[''comms''][''telephone'']@

\\text{22}{55}{50}{
\\begin{tabular}{ll}
\\textbf{Patient:} & @"%(title)s %(first)s %(last)s" % patient.get_names ()@ \\\\
& @"%(number)s %(street)s" % patient[''addresses''][''home'']@ \\\\
& @"%(city)s %(postcode)s" % patient[''addresses''][''home'']@ \\\\
DOB: & @patient.getDOB ().Format (''%x'')@ \\\\
@patient[''comms''].has_key (''telephone'') and ''PHONE: & %s\\\\\\\\'' % patient[''comms''][''telephone'']@
\\end{tabular}
}
\\text{22}{85}{100}{
\textbf{REQUEST FOR @type@}\\\\
@request@\\
\\\\
\\ifnum@len (therapy)@>0
\\textbf{THERAPY}\\\\
@therapy@\\\\
\\fi
\\
\\ifnum@len (clinical_notes)@>0
\\textbf{CLINICAL NOTES}\\
@clinical_notes@\\
}

\\ifnum@copy_to is not None@>0
\text{133}{85}{55}{
\textbf{Copy of report to:}\\
\\
@copy_to and ''%(title)s %(firstnames)s %(lastnames)s'' % copy_to.get_names ()@\\\\
@copy_to and ''%(number)s %(street)s, %(city)s %(postcode)s'' % copy_to[''addresses''][''work'']@\\\\
@copy_to and copy_to[''comms''].has_key (''fax'') and ''FAX: %s'' % copy_to[''comms''][''fax'']@\\\\
}
\\fi
\\text{130}{107}{60}{
\\begin{multicols}{2}
\\checkbox{@routine@} Routine\\\\
\\checkbox{@urgent@} Urgent\\\\\
\\checkbox{@fax_result@} Fax result\\\\
\\checkbox{@phone_result@} Phone result\\\\
\\checkbox{@pensioner@} Pensioner\\\\
\\checkbox{@patient[''ext id''].has_key (''Repat No.'')@} Veteran\\\\
\\checkbox{@referral_pad@} Referral pads\\\\
\\end{multicols}
}

\\text{22}{140}{165}{
\\textbf{PATIENT INSTRUCTIONS}\\\\

@instructions@}

\\text{133}{225}{55}{
\\textbf{Doctor''s Signature}
}

\\text{57}{260}{80}{GNUMed v0.1.0}

\\end{page}
\\end{document}
');

insert into form_fields (fk_form, long_name, template_placeholder, help, fk_type, param, display_order ) values
( 3, 'Request', 'request', 
  'The services requested', 
  4,
  NULL, 1);

insert into form_fields (fk_form, long_name, template_placeholder, help, fk_type, param, display_order ) values
( 3, 'Clinical Notes', 'clinical_notes', 
  '', 
  4,
  NULL, 2);

insert into form_fields (fk_form, long_name, template_placeholder, help, fk_type, param, display_order ) values
( 3, 'Therapy', 'therapy', 
  'Description of patient''s current therapy', 
  4,
  NULL, 3);

insert into form_fields (fk_form, long_name, template_placeholder, help, fk_type, param, display_order ) values
( 3, 'Patient Instructions', 'instructions', 
  'Instructions for the Patient', 
  4,
  NULL, 4);

insert into form_fields (fk_form, long_name, template_placeholder, help, fk_type, param, display_order ) values
( 3, 'Routine', 'routine', 
  'Routine request', 
  3,
  NULL, 5);

insert into form_fields (fk_form, long_name, template_placeholder, help, fk_type, param, display_order ) values
( 3, 'Urgent', 'urgent', 
  '', 
  3, NULL, 6);

insert into form_fields (fk_form, long_name, template_placeholder, help, fk_type, param, display_order ) values
( 3, 'Fax result', 'fax_result', 
  '', 
  3, NULL, 7);

insert into form_fields (fk_form, long_name, template_placeholder, help, fk_type, param, display_order ) values
( 3, 'Phone result', 'phone_result', 
  '', 
  3, NULL, 8);

insert into form_fields (fk_form, long_name, template_placeholder, help, fk_type, param, display_order ) values
( 3, 'Pensioner', 'pensioner', 
  'Patient is a pensioner (i.e. asking referree for discount)', 
  3, NULL, 9);

insert into form_fields (fk_form, long_name, template_placeholder, help, fk_type, param, display_order ) values
( 3, 'Referral pads', 'referral_pad', 
  '', 
  3, NULL, 10);

insert into form_fields (fk_form, long_name, template_placeholder, help, fk_type, param, display_order ) values
( 3, 'Type', 'type', 
  'The clinical discipline of the referree', 
  2, 'Pathology
Radiology
Vascular
Cardiology
Neurophysiology
Respiratory
Nuclear Medicine
Audiology
Physiotherapy
Occupational Therapy', 11);
-- these referral types must match entries in org_category.description in the demographics service.


