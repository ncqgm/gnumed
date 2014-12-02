-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
delete from ref.keyword_expansion where keyword = 'score-LQTS-Schwartz';

insert into ref.keyword_expansion (
	fk_staff,
	keyword,
	textual_data
) values (
	null,
	'score-LQTS-Schwartz',
'Schwartz-Score: Long-QT-Syndrome Clinical Probability Score
--------------------------------------------------------------
Taggart NW, et al.: Diagnostic Miscues in Congenital Long-QT Syndrome.
Circulation. 2007; 115:2613-2620; DOI: 10.1161/circulationaha.106.661082.

History:
1) $[0/1/2]$ History of syncope (with stress = 2, without stress = 1)
	(Syncope and Torsades de Pointes mutually exclusive)
2) $[0/1]$ Congenital deafness

Family history (cannot count same family member in both):
3) $[0/1]$ family member with definite LQTS
4) $[0/0.5]$ Unexplained sudden death in 1st-degree family member <30 years

ECG:
5) Corrected QT (QTc by Bazett''s formula)
   $[0/1/3/3]$ 450 in males: 1; 460-470: 2; >470: 3
6) $[0/2]$ Torsades de pointes
7) $[0/1]$ T-wave alternans
8) $[0/1]$ > 3 leads with notched T waves
9) $[0/0.5]$ Bradycardia (< 2nd percentile for age)

Sum: $[Sum]$

	  0: low probability
	1-3: intermediate probability
	 >3: high probability
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-LQTS_Score.sql', '20.0');
