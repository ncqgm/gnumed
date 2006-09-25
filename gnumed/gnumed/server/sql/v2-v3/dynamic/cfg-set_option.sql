-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - add set_option functions
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: cfg-set_option.sql,v 1.1 2006-09-25 10:55:01 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
begin;

-- --------------------------------------------------------------
create or replace function cfg.create_cfg_item(text, text, text, text, text)
	returns integer
	language 'plpgsql'
	as '
declare
	_option alias for $1;
	_val_type alias for $2;
	_workplace alias for $3;
	_cookie alias for $4;
	_owner alias for $5;
	real_owner text;
	pk_template integer;
	pk_item integer;
begin
	-- check template
	select into pk_template pk from cfg.cfg_template where name = _option and type = _val_type;
	if not FOUND then
		insert into cfg.cfg_template (name, type) values (_option, _val_type);
		select into pk_template currval(''cfg.cfg_template_pk_seq'');
	end if;

	if _owner is null then
		select into real_owner CURRENT_USER;
	else
		real_owner := _owner;
	end if;

	-- check item
	if _cookie is NULL then
		select into pk_item pk from cfg.cfg_item where
			fk_template = pk_template and
			owner = real_owner and
			workplace = _workplace and
			cookie is null;
	else
		select into pk_item pk from cfg.cfg_item where
			fk_template = pk_template and
			owner = real_owner and
			workplace = _workplace and
			cookie = _cookie;
	end if;
	if FOUND then
		return pk_item;
	end if;

	insert into cfg.cfg_item (
		fk_template, workplace, cookie, owner
	) values (
		pk_template,
		_workplace,
		_cookie,
		real_owner
	);
	select into pk_item currval(''cfg.cfg_item_pk_seq'');

	return pk_item;
end;';


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
	if _value is of (text, char, varchar, name) then
		val_type := ''string'';
	elsif _value is of (smallint, integer, bigint, numeric, boolean) then
		val_type := ''numeric'';
	elsif _value is of (bytea) then
		val_type := ''data'';
	elsif _value is of (text[]) then
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
select public.log_script_insertion('$RCSfile: cfg-set_option.sql,v $', '$Revision: 1.1 $');

-- --------------------------------------------------------------
commit;

-- ==============================================================
-- $Log: cfg-set_option.sql,v $
-- Revision 1.1  2006-09-25 10:55:01  ncq
-- - added here
--
-- Revision 1.3  2006/09/21 19:54:47  ncq
-- - we don't need set_option2()
--
-- Revision 1.2  2006/09/21 19:51:43  ncq
-- - eventually make set_option() work
--
-- Revision 1.1  2006/09/19 18:27:47  ncq
-- - add cfg.set_option()
-- - drop NOT NULL on cfg.cfg_item.cookie
--
-- Revision 1.3  2006/09/18 17:32:53  ncq
-- - make more fool-proof
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
