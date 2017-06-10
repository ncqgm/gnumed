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
comment on table clin.lnk_loinc2test_panel is 'Links LOINC codes to test panels which thusly become part of said panel.';

select audit.register_table_for_auditing('clin', 'lnk_loinc2test_panel');
select gm.register_notifying_table('clin', 'lnk_loinc2test_panel');

-- table constraints
drop index if exists clin.idx_ll2tp_uniq_l_per_p cascade;
create unique index idx_ll2tp_uniq_l_per_p on clin.lnk_loinc2test_panel(fk_test_panel, loinc);

-- grants
grant select on clin.lnk_loinc2test_panel to "gm-public";
grant select, insert, update, delete on clin.lnk_loinc2test_panel to "gm-doctors";
grant usage on clin.lnk_loinc2test_panel_pk_seq to "gm-doctors";

-- --------------------------------------------------------------
-- .fk_test_panel
comment on column clin.lnk_loinc2test_panel.fk_test_panel is 'FK linking the test panel';

alter table clin.lnk_loinc2test_panel
	alter column fk_test_panel
		set not null;

alter table clin.lnk_loinc2test_panel drop constraint if exists clin_ll2tp_fk_test_panel cascade;

alter table clin.lnk_loinc2test_panel
	add constraint clin_ll2tp_fk_test_panel
		foreign key (fk_test_panel) references clin.test_panel(pk)
			on update cascade
			on delete cascade
;

-- --------------------------------------------------------------
-- .loinc
comment on column clin.lnk_loinc2test_panel.loinc is 'LOINC to include in test panel';

alter table clin.lnk_loinc2test_panel drop constraint if exists clin_ll2tp_sane_loinc cascade;

alter table clin.lnk_loinc2test_panel
	add constraint clin_ll2tp_sane_loinc check (
		gm.is_null_or_blank_string(loinc) is False
	);

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-lnk_loinc2test_panel-dynamic.sql', '22.0');
