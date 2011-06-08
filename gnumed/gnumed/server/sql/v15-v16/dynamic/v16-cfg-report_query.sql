-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
delete from cfg.report_query where label = 'patients whose narrative contains a certain coded term';

delete from cfg.report_query where label = 'patients whose EMR contains a certain coded term';
insert into cfg.report_query (label, cmd) values (
	'patients whose EMR contains a certain coded term',
'select
	*
from
	clin.v_linked_codes c_vlc
		inner join clin.v_pat_items d_vpi on (d_vpi.pk_item = c_vlc.pk_item)
			inner join dem.v_basic_person d_vbp on (d_vbp.pk_identity = d_vpi.pk_patient)
where
	c_vlc.code = ''put the code here''
	-- specify a coding system here
--	and c_vlc.name_long = ''...''
	-- specify a SOAP category here
--	and c_vpi.soap_cat = ''...''
');


-- --------------------------------------------------------------
select gm.log_script_insertion('v16-cfg-report_query.sql', 'Revision: v16');

-- ==============================================================
