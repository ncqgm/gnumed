-- Project: GnuMed - service "Reference" -- Australian specific stuff
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/au/gmReference.sql,v $
-- $Revision: 1.3 $
-- license: GPL
-- author: Ian Haywood

-- This file populates the tables in the reference service with Australian-specific content.
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================

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
