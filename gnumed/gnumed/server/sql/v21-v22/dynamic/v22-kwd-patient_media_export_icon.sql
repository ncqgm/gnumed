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
delete from ref.keyword_expansion where keyword = '$$gnumed_patient_media_export_icon';

insert into ref.keyword_expansion (
	fk_staff,
	keyword,
	textual_data
) values (
	null,
	'$$gnumed_patient_media_export_icon',
	'$$gnumed_patient_media_export_icon'
);


-- --------------------------------------------------------------
delete from ref.keyword_expansion where keyword = '$$gnumed_patient_media_export_icon_2';

insert into ref.keyword_expansion (
	fk_staff,
	keyword,
	textual_data
) values (
	null,
	'$$gnumed_patient_media_export_icon_2',
	'$$gnumed_patient_media_export_icon_2'
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-kwd-patient_media_export_icon.sql', '22.0');
