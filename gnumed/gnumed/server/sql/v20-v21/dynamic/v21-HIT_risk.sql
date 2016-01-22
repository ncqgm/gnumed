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
delete from ref.keyword_expansion where keyword = 'algo-HIT';

insert into ref.keyword_expansion (
	fk_staff,
	keyword,
	textual_data
) values (
	null,
	'algo-HIT',
'HIT risk assessment
-----------------------------------------------------------
Chest / 141 / 2 / February, 212 Supplement / e499S
"Treatment and Prevention of Heparin-Induced Thrombocytopenia"

Indication: $[indication for Hep/LMWH]$
Exposure >4d: $[>4d exposure: Yes/No]$
Substance: $[name of Hep/LWMH]$

HIT risk in postoperative patients:
   1-5% -- Heparin, any dose
 0.1-1% -- Heparin, flushes (case reports only)
 0.1-1% -- LMWH, any dose
   1-3% -- cardiac surgery (?Heparin)

HIT risk in non-surgical patients:
     1% -- cancer (?Heparin)
 0.1-1% -- Heparin, any dose
  <0.1% -- Heparin, flushes
   0.6% -- LMWH, any dose
   0.4% -- ICU (?Heparin)
  <0.1% -- Obstetrics (?Heparin)

(risk of HIT from Heparin generally 10x that of HIT from LMWH)

Risk estimate: $[risk estimate]$

If risk > 1% platelet monitoring every 2-3 days from
day 4 to day 14 or until exposure stops is suggested.

No monitoring is suggested if the risk is < 1%.

Monitor: $[Monitor ?  Yes/No]$

Diagnostic hints:
 typically at 5-10 days after begin of exposure platelets fall to
   < 150x10^9/l
     (occurs in 85-90% of patients developing HIT)
 or to
   30-50% of pre-exposure value even if > 150x10^9/l
     (occurs in 90-95% of patients developing HIT)
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-HIT_risk.sql', '21.0');
