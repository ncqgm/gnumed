-- Project: GnuMed - service "Reference" -- Australian specific stuff
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/au/gmReference.sql,v $
-- $Revision: 1.6 $
-- license: GPL
-- author: Ian Haywood

-- This file populates the tables in the reference service with Australian-specific content.
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================


insert into form_types (name) values ('radiology');
insert into form_types (name) values ('pathology');
insert into form_types (name) values ('vascular');
  
insert into form_defs (pk, name_short, name_long, revision, engine, template) values
(1,
 'Standard Referral', 'Standard specialist referral letter for AU', 1, 'L', 
 '\\documentclass{letter}
\\address{ @"%(title)s %(first)s %(last)s" % sender.get_names ()@ \\\\ 
@"%(number)s %(street)s" % sender.getAddresses (''work'', 1)@ \\\\
@"%(urb)s %(postcode)s" % sender.getAddresses (''work'', 1)@ \\\\}
\\signature{ @"%(title)s %(first)s %(last)s" % sender.get_names ()@}
\\begin{document}
\\begin{letter}{@"%(title)s %(first)s %(last)s" % recipient.get_names ()@ \\\\ 
@"%(number)s %(street)s" % recipient_address@ \\\\
@"%(urb)s %(postcode)s" % recipient_address@ \\\\} }

\\opening{Dear @"%(title)s %(first)s %(last)s" % recipient.get_names ()@ }

\\textbf{Re:} @"%(first)s %(last)s" % patient.get_names ()@, 
@"%(number)s %(street)s, %(urb)s %(postcode)s" % patient.getAddresses (''home'', 1)@, 
DOB: @patient.getDOB ().Format (''%x'')@

@text@

\\ifnum@flags[''include_meds'']@>0
\\textbf{Medications List}

\\begin{tabular}{lll}
@[[med[''drug''], med[''dose''], med[''direction'']] for med in clinical.getMedicationsList ()]@
\\end{tabular}
\\fi

\\ifnum@flags[''include_pasthx'']@>0
\\textbf{Disease List}

\\begin{tabular}{ll}
@[[phx[''diagnosis''], phx[''started'']] for phx in clinical.getPastHistory ()]@
\\end{tabular}
\\fi

\\closing{Yours sincerely,}

\\end{letter}
\\end{document}');

insert into form_defs (pk, name_short, name_long, revision, engine, template) values
(2, 
 'E-mail Referral', 'E-mail referral letter for Australia', 1, 'T',
-- WARNING: no standard for this actually exists in AU!
-- this is for demonstration purposes only 
'Re:  @"%(first)s %(last)s" % patient.get_names ()@ 
      @"%(number)s %(street)s, %(urb)s %(postcode)s" % patient.getAddresses (''home'', 1)@, 
      DOB: @patient.getDOB ().Format (''%x'')@

@text@

@(flags[''include_meds''] and "Medications") or ''''@
@(flags[''include_meds''] and [[med[''drug''], med[''dose''], med[''direction'']] for med in clinical.getMedicationsList ()]) or ''''@

@(flags[''include_phx''] and "Past History") or ''''@
@(flags[''include_phx''] and [[phx[''diagnosis''], phx[''started'']] for phx in clinical.getPastHistory ()]) or ''''@
');



insert into form_defs (pk, name_short, name_long, revision, engine, template) values
(3, 
'PBS Script', 'Prescription using the standard form of the Pharmaceutical Benefits Scheme', 1, 'L',
'\\documentclass{a4form}
\\usepackage{multicol}
% this is a template of a *community* PBS script form
% (hospital scripts are completely different and must be handwritten [sob])

\\begin{document}
\\begin{page}
\\text{25}{25}{80}{@sender.getExternalID ("Prescriber No.")@}
\\text{130}{25}{80}{@sender.getExternalID ("Prescriber No.")@}

\\text{35}{33}{80}{@patient.getExternalID ("Repat No.") or patient.getExternalID ("Medicare No.")@}
\\text{140}{33}{80}{@patient.getExternalID ("Repat No.") or patient.@getExternalID ("Medicare No.")@}
% use the Department of Veteran''s affairs number if available: these patients get extra benefits

\\text{24}{57}{80}{@"%(first)s %(last)s" % patient.get_names ()@}
\\text{129}{57}{80}{@"(first)s %(last)s" % patient.get_names ()@}

\\text{15}{60}{80}{@"%(number)s %(street)s, %(urb)s %(postcode)s" % patient.getAddresses (''home'', 1)@}
\\text{120}{60}{80}{@"%(number)s %(street)s, %(urb)s %(postcode)s" % patient.getAddresses (''home'', 1)@}

\\text{9}{72}{50}{\\today}
\\text{114}{72}{50}{\\today}

\\ifnum@patient.getExternalID ("Repat No.") is not None@>0
\\text{27}{77}{10}{X} % mark as RPBS script
\\text{132}{77}{10}{X}
\\else
\\text{7}{77}{10}{X} % ordinary PBS
\\text{112}{77}{10}{X}
\\fi

\\ifnum@flags[''no_brand_substitution'']>0
\\text{43}{74.5}{7}{X}
\\text{148}{74.5}{7}{X}
\\fi

\\text{22.5}{84}{82.5}{
% TODO: drugs business objects yet to be written
\\vspace{1cm}
\\hspace{1cm} @"%(title)s %(first)s %(last)s" % sender.get_names ()@
}

\\text{127.5}{84}{82.5}{
% TODO: drugs business objects yet to be written
\\vspace{1cm}
\\hspace{1cm} @"%(title)s %(first)s %(last)s" % sender.get_names ()@
}
\\end{page}
\\end{document}');

insert into form_defs (pk, name_short, name_long, revision, engine, template) values
(4,
 'Basic request', 'A proof-of-concept basic request form', 1, 'L', 
 '\\documentclass[12pt]{article}
\\begin{document}

\\begin{tabular}{ll}
\\textbf{Sender:} & @"%(title)s %(first)s %(last)s" % sender.get_names ()@ \\\\
& @"%(number)s %(street)s" % sender.getAddresses (''work'', 1)@ \\\\
& @"%(urb)s %(postcode)s" % sender.getAddresses (''work'', 1)@ \\\\
\\end{tabular}

\\begin{tabular}{ll}
\\textbf{Patient:} & @"%(title)s %(first)s %(last)s" % patient.get_names ()@ \\\\
& @"%(number)s %(street)s" % patient.getAddresses (''home'', 1)@ \\\\
& @"%(urb)s %(postcode)s" % patient.getAddresses (''home'', 1)@ \\\\
DOB: & @patient.getDOB ().Format (''%x'')@ \\\\
\\end{tabular}

\\textbf{Request:}  @request@


\\textbf{Clinical Notes:} @clinical_notes@


\\ifnum@len (instructions)@>0
\\textbf{Patient Instructions:} 
@instructions@
\\fi

\\end{document}');