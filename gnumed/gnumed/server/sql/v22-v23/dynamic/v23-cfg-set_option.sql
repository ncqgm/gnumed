-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;
set check_function_bodies to on;

-- --------------------------------------------------------------
create or replace function cfg.set_option(text, anyelement, text, text, text)
	returns boolean
	language 'plpgsql'
	as '
declare
	_option alias for $1;
	_value alias for $2;
	_workplace alias for $3;
	_cookie alias for $4;
	_owner alias for $5;
	val_type text;
	pk_item integer;
	rows integer;
	cmd text;
begin
	-- determine data type
	if pg_typeof(_value) in (''text''::regtype, ''char''::regtype, ''varchar''::regtype, ''name''::regtype) then
		val_type := ''string'';
	elsif pg_typeof(_value) in (''smallint''::regtype, ''int''::regtype, ''bigint''::regtype, ''numeric''::regtype, ''boolean''::regtype) then
		val_type := ''numeric'';
	elsif pg_typeof(_value) in (''bytea''::regtype) then
		val_type := ''data'';
	elsif pg_typeof(_value) in (''text[]''::regtype) then
		val_type := ''str_array'';
	else
		raise exception ''cfg.set_option(text, any, text, text, text): invalid type of value'';
	end if;

	-- create template/item if need be
	select into pk_item cfg.create_cfg_item(_option, val_type, _workplace, _cookie, _owner);

	-- set item value
	cmd := ''select 1 from cfg.cfg_'' || val_type || '' where fk_item='' || pk_item || '';'';
	execute cmd;
	get diagnostics rows = row_count;
	found := rows <> 0;

	if FOUND then
		if val_type = ''str_array'' then
			cmd := ''update cfg.cfg_str_array set value=''''{"'' || array_to_string(_value, ''","'') || ''"}'''' where fk_item='' || pk_item || '';'';
		elsif val_type = ''data'' then
			cmd := ''update cfg.cfg_data set value='''''' || encode(_value, ''escape'') || '''''' where fk_item='' || pk_item || '';'';
		else
			cmd := ''update cfg.cfg_'' || val_type || '' set value='' || quote_literal(_value) || '' where fk_item='' || pk_item || '';'';
		end if;
		execute cmd;
		return True;
	end if;

	if val_type = ''str_array'' then
		cmd := ''insert into cfg.cfg_str_array(fk_item, value) values ('' || pk_item || '', ''''{"'' || array_to_string(_value, ''","'') || ''"}'''');'';
	elsif val_type = ''data'' then
		cmd := ''insert into cfg.cfg_data(fk_item, value) values ('' || pk_item || '', '''''' || encode(_value, ''escape'') || '''''');'';
	else
		cmd := ''insert into cfg.cfg_'' || val_type || '' (fk_item, value) values ('' || pk_item || '', '' || quote_literal(_value) || '');'';
	end if;
	execute cmd;
	return True;
end;';

comment on function cfg.set_option(text, anyelement, text, text, text) is
	'set option, owner = NULL means CURRENT_USER';

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-cfg-set_option.sql', 'v23');
