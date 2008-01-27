-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-clin-coded_phrase.sql,v 1.1 2008-01-27 21:06:00 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function audit.ft_del_coded_narrative() cascade;
drop function audit.ft_upd_coded_narrative() cascade;
drop function audit.ft_ins_coded_narrative() cascade;
\set ON_ERROR_STOP 1

select audit.add_table_for_audit('clin', 'coded_phrase');
delete from audit.audited_tables where schema = 'clin' and table_name = 'coded_narrative';

comment on table clin.coded_phrase is
	'associates codes with text snippets
	 which may be in use in clinical tables';
comment on column clin.coded_phrase.term is
	'the text snippet that is to be coded';
comment on column clin.coded_phrase.code is
	'the code in the coding system';
comment on column clin.coded_phrase.xfk_coding_system is
	'the coding system used to code the text snippet';



\unset ON_ERROR_STOP
drop view clin.v_coded_phrases cascade;
\set ON_ERROR_STOP 1

create view clin.v_coded_phrases as

select
	term,
	code,
	xfk_coding_system as coding_system
from
	clin.coded_phrase

	union

select
	term,
	code,
	coding_system
from
	ref.v_coded_terms
;

grant select on clin.v_coded_phrases to group "gm-doctors";



\unset ON_ERROR_STOP
drop function clin.add_coded_term(text, text, text) cascade;
\set ON_ERROR_STOP 1

create or replace function clin.add_coded_phrase(text, text, text) returns boolean as '
declare
	_term alias for $1;
	_code alias for $2;
	_system alias for $3;
	_tmp text;
begin
	select into _tmp 1 from clin.coded_phrase where
		term = _term
		and code = _code
		and xfk_coding_system = _system;

	if found then
		return True;
	end if;

	insert into clin.coded_phrase (term, code, xfk_coding_system)
		values (_term, _code, _system);
	return True;
end;' language 'plpgsql';


-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-coded_phrase.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-clin-coded_phrase.sql,v $
-- Revision 1.1  2008-01-27 21:06:00  ncq
-- - new
--
--