-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;
-- --------------------------------------------------------------
delete from ref.keyword_expansion where keyword = 'GKV_Stempel-LaTeX_picture_environment';

insert into ref.keyword_expansion (
	fk_staff,
	keyword,
	textual_data
) values (
	null,
	'GKV_Stempel-LaTeX_picture_environment',
	'%----- Stempel für LMcC ---------------
% da der Stempel in verschiedenen Forumularen an verschiedenen
% Stellen gesetzt wird, wird hier mit einem Offset gearbeitet,
% -> nur der Offset ist (im Formulartemplate !) anzupassen, z.B.:
%\stempeloffsetx=17
%\stempeloffsety=-80

% debug:
%\put(\stempeloffsetx,\stempeloffsety){.+ (Stempelwurzel)}

\put(\stempeloffsetx,\stempeloffsety){{\tiny BSNR:$<praxis_id::KV-BSNR//KV//%(value)s::25>$ / LANR:$<current_provider_external_id::%s//KV-LANR//KV::25>$}}

\advance\stempeloffsety by -4
\put(\stempeloffsetx,\stempeloffsety){$<current_provider::::40>$, {\small FA für $<current_provider_external_id::%s//Fachgebiet//Ärztekammer::50>$}}

\advance\stempeloffsety by -5
\put(\stempeloffsetx,\stempeloffsety){{\tiny $<praxis::%(praxis)s: %(branch)s::100>$}}

\advance\stempeloffsety by -5
\put(\stempeloffsetx,\stempeloffsety){{\tiny $<praxis_address::%(street)s %(number)s::80>$}}

\advance\stempeloffsety by -5
\put(\stempeloffsetx,\stempeloffsety){{\tiny $<praxis_address::%(postcode)s %(urb)s::80>$}}

\advance\stempeloffsety by -5
\put(\stempeloffsetx,\stempeloffsety){{\small $<praxis_comm::workphone//fon %(url)s::80>$; $<praxis_comm::fax//fax %(url)s::80>$; $<praxis_comm::email//%(url)s::80>$}}
%----- Stempel ---------------
'
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-GKV_Stempel.sql', '20.0');
