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

$[BIL in mg/dl]$ Bilirubin (mg/dl)
$[CREA in mg/dl (between 1 and 4)]$ Serum Creatinine (mg/dl)
$[INR]$ International Normalized Ratio (INR), min 1.0

(	0.643 +
	0.957 x ln(CREA) +
	0.378 x ln(BIL) +
	1.12 x ln(INR)
) x 10

Result: $[Apply formula !]$

Score    :   6  15  20  24  28  30  35  40
% 3-month
mortality:   1   5  11  21  37  49  80  98

--------------------------------------
For SI units (µmol/l):

10 x 
(	0.643 +
	0.957 x ln(CREA / 88.4) +
	0.378 x ln(BIL / 88.4) +
	1.12 x ln(INR)
)');

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-ref-MELD_score-fixup.sql', '18.2');
