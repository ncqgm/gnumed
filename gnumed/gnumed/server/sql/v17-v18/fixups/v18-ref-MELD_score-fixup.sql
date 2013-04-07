-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: sebastian.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
set client_encoding to 'utf-8';

delete from ref.keyword_expansion where keyword = 'score-MELD-liver';

insert into ref.keyword_expansion (
	fk_staff,
	keyword,
	textual_data
) values (
	null,
	'score-MELD-liver',
'MELD-Score for End Stage Liver Disease
--------------------------------------
Wiesner R et al. The model for end-stage liver disease (MELD) and allocation of donor livers. Gastroenterology 2003; 124: 91–6

BIL:   $[BIL in mg/dl]$ mg/dl (Bilirubin)
CREA:  $[CREA in mg/dl]$ mg/dl (Serum Creatinine, 1-4)
INR:   $[INR]$ (International Normalized Ratio, >= 1.0)

(	0.643 +
	0.378 x ln(BIL) +
	0.957 x ln(CREA) +
	1.12 x ln(INR)
) x 10

Result: $[Apply formula !]$

3-month mortality in %
----------------------
Score   %
  6     1
 15     5
 20    11
 24    21
 28    37
 30    49
 35    80
 40    98

--------------------------------------
For SI units (µmol/l):

10 x 
(	0.643 +
	0.378 x ln(BIL / 88.4) +
	0.957 x ln(CREA / 88.4) +
	1.12 x ln(INR)
)');

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-ref-MELD_score-fixup.sql', '18.2');
