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
delete from ref.keyword_expansion where keyword = 'GKV_KVK_Daten-LaTeX_picture_environment';

insert into ref.keyword_expansion (
	fk_staff,
	keyword,
	textual_data
) values (
	null,
	'GKV_KVK_Daten-LaTeX_picture_environment',
	'%----- KVK-Daten als GKV-formatierter Block ---------------
% \ganzlinks muß definiert sein
% dieser Block setzt eine LaTeX-"picture"-Umgebung voraus,
% die "rechts unten" als 0,0 definiert hat,
% dieser Block beinhaltet Referenzen auf Sekundärplatzhalter,
% die erst beim Zweitdurchlauf ersetzt werden

% KVK-Daten:
%\put(\ganzlinks,38){\texttt{*KVKKrankenkasse*}}
\put(\ganzlinks,30){\texttt{$<name::%(lastnames)s, %(firstnames)s::50>$}}
\put(-20,25){\texttt{$<date_of_birth::%d.%m.%Y::10>$}}
\put(\ganzlinks,25){\texttt{$<adr_street::KVK::25>$ $<adr_number::KVK::5>$}}
\put(\ganzlinks,20){\texttt{$<adr_postcode::KVK::5>$ $<adr_location::KVK::30>$}}
%\put(\ganzlinks,10){\texttt{*KVKKassenNr*}}
%\put(-56,10){\texttt{*KVKVersichertenNr*}}
%\put(-22,10){\texttt{*KVKStatus*}}
%\put(\ganzlinks,2){\texttt{*KVKZa-KZVNr*}}
%\put(-49,2){\texttt{*KVKVKgueltigbis*}}
\put(-24,2){\texttt{$<today::%d.%m.%Y::10>$}}

% --- debugging ---
% links oben
\put(\ganzlinks,43){.+}
\put(\ganzlinks,37){.+}

% rechts oben
\put(0,37){.+}
\put(0,43){.+}

% links unten:
\put(\ganzlinks,0){.+ (LU: -80,0)}
% rechts unten (Ursprungskoordinate (rechte untere Ecke KVK-Datenblock))
\put(0,0){.+ (RU: 0,0)}

%\put(0,-47){.+ (0,-47)}
%\put(\ganzlinks,0){.+ (-80,0)}
%\put(\ganzlinks,-47){.+ (-80,-47)}
% --- debugging ---

%----- KVK-Daten als GKV-formatierter Block ---------------
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-GKV_formatierte_KVK_Daten.sql', '18.0');
