-- Project: GnuMed - service "Reference" -- Australian specific stuff
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/au/gmReference.sql,v $
-- $Revision: 1.4 $
-- license: GPL
-- author: Ian Haywood

-- This file populates the tables in the reference service with Australian-specific content.
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================


-- this form is for nice laTeX referral letters
-- accepts a dictionary of the following values
-- (all strings unless otherwise specified)
-- SENDER: the sender's name
-- SENDERADDRESS: [multiline]: the sender's address
-- RECIPIENT: the recipient's name
-- RECIPIENTADDRESS: you get the idea
-- PATIENTNAME
-- PATIENTADDRESS
-- DOB: the patient's date of birth
-- TEXT: free text of the clinical notes. Paragraphs marked by double lines
-- [integer] INCLUDEMEDS: nonzero if meds should be included
-- [string list] MEDNAME: names of medications
-- [string list] MEDFORM: form of medication
-- [string list] MEDDOSE: dose of medication
-- [integer] INCLUDEPASTHX: nonzero if past history is to be included
-- [string list] PASTHX: past history disgnoses
-- [string list] PASTHXBEGAN: when the diagnosis began  
insert into form_defs (pk, name_short, name_long, revision, engine, template) values
(1,
 'Standard Referral', 'Standard specialist referral letter for AU', 1, 'L', 
 '\\documentclass{letter}
\\address{ @SENDER \\\\ @SENDERADDRESS }
\\signature{@SENDER }
\\begin{document}
\\begin{letter}{@RECIPIENT \\\\ @RECIPIENTADDRESS }
\\opening{Dear @RECIPIENT}
\\textbf{Re:} @PATIENTNAME, DOB: @DOB, @PATIENTADDRESS 

@TEXT

\\ifnum@INCLUDEMEDS>0
\\textbf{Medications List}
\\begin{tabular}{lll}
@MEDNAME & @MEDFORM & @MEDDOSE \\\\
\\end{tabular}
\\fi

\\ifnum@INCLUDEPASTHX>0
\\textbf{Disease List}

\\begin{tabular}{ll}
@PASTHX & @PASTHXBEGAN \\\\
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
'To: @RECIPIENT <@RECIPIENTADDRESS>
From: @SENDER <@SENDERADDRESS>

Re: @PATIENT, @PATIENTADDRESS

@TEXT
');


-- this is a form to print PBS scripts
-- note this requires the "a4form" LaTeX extension, in gnumed CVS under gnumed/test-area/ian/a4form.cls
-- parameters:
-- PRESCRIBERNO: prescriber's 6-digit HIC prescriber number
-- PRESCRIBERNAME: prescriber's full name and academic title
-- MEDICARENO: patient's medicare number
-- PATIENTNAME: patient's name
-- PATIENTADDRESS: patient's address (can have newlines)
-- [inetger] RPBS: nonzero if this a Repatriation script
-- [integer] BRAND: nonzero for no brand substitution
-- [string list] DRUG: list of drugs
-- [string list] FORM: drug strength and form
-- [string list] DOSE: frequency of taking
-- [string list] QUANTITY: quantity of drug 
insert into form_defs (pk, name_short, name_long, revision, engine, template) values
(3, 
'PBS Script', 'Prescription using the standard form of the Pharmaceutical Benefits Scheme', 1, 'L',
'\\documentclass{a4form}
\\usepackage{multicol}
% this is a template of a *community* PBS script form
% (hospital scripts are completely different and must be handwritten [sob])

\\begin{document}
\\begin{page}
\\text{25}{25}{80}{@PRESCRIBERNO}
\\text{130}{25}{80}{@PRESCRIBERNO}

\\text{35}{33}{80}{@MEDICARENO}
\\text{140}{33}{80}{@MEDICARENO}

\\text{24}{57}{80}{@PATIENTNAME}
\\text{129}{57}{80}{@PATIENTNAME}

\\text{15}{60}{80}{@PATIENTADDRESS}
\\text{120}{60}{80}{@PATIENTADDRESS}

\\text{9}{72}{50}{\\today}
\\text{114}{72}{50}{\\today}

\\ifnum@RPBS>0
\\text{27}{77}{10}{X}
\\text{132}{77}{10}{X}
\\else
\\text{7}{77}{10}{X}
\\text{112}{77}{10}{X}
\\fi

\\ifnum@BRANDONLY>0
\\text{43}{74.5}{7}{X}
\\text{148}{74.5}{7}{X}
\\fi

\\text{22.5}{84}{82.5}{
@DRUG \\\\ \\hspace{0.5cm}@FORM \\\\ \hspace{0.7cm}@DOSE \\\\ \\hspace{0.7cm}@QUANTITY \\\\\

\\vspace{1cm}
\\hspace{1cm} @PRESCRIBERNAME
}

\\text{127.5}{84}{82.5}{
@DRUG \\\\ \\hspace{0.5cm}@FORM \\\\ \hspace{0.7cm}@DOSE \\\\ \\hspace{0.7cm}@QUANTITY \\\\\

\\vspace{1cm}
\\hspace{1cm} @PRESCRIBERNAME
}
\\end{page}
\\end{document}');
