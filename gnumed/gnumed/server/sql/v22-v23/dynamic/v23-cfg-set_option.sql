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
drop function if exists cfg.create_cfg_item(text, text, text, text, text);
drop function if exists cfg.create_cfg_item(IN _option text, IN _workplace text, IN _cookie text, IN owner text, IN _description text);

create or replace function cfg.create_cfg_item(IN _option text, IN _workplace text, IN _cookie text, IN _owner text, IN _description text)
	returns integer
	language 'plpgsql'
	as '
declare
	__pk_template integer;
	__pk_item integer;
begin
	-- check template
	select into __pk_template pk from cfg.cfg_template where name = _option;
	if not FOUND then
		insert into cfg.cfg_template (name) values (_option) returning pk INTO __pk_template;
	end if;
	IF _description IS NOT NULL THEN
		UPDATE cfg.cfg_template
		SET description = _description
		WHERE pk = __pk_template;
	END IF;
	IF trim(_owner) = '''' THEN
		SELECT CURRENT_USER into _owner;
	END IF;
	-- check item
	if _cookie is NULL then
		select into __pk_item pk from cfg.cfg_item where
			fk_template = __pk_template and
			owner = _owner and
			workplace = _workplace and
			cookie is null;
	else
		select into __pk_item pk from cfg.cfg_item where
			fk_template = __pk_template and
			owner = _owner and
			workplace = _workplace and
			cookie = _cookie;
	end if;
	if FOUND then
		return __pk_item;
	end if;

	insert into cfg.cfg_item (
		fk_template, workplace, cookie, owner
	) values (
		__pk_template,
		_workplace,
		_cookie,
		_owner
	) returning pk_item into __pk_item;
	return __pk_item;
end;';

-- --------------------------------------------------------------
drop function if exists cfg.set_option(text, anyelement, text, text, text);
drop function if exists cfg.set_option(IN _option text, IN _value anyelement, IN _workplace text, IN _cookie text, IN _owner text, IN _description text);

create or replace function cfg.set_option(IN _option text, IN _value anyelement, IN _workplace text, IN _cookie text, IN _owner text, IN _description text)
	returns boolean
	language 'plpgsql'
	as '
declare
	pk_item integer;
begin
	SELECT INTO pk_item cfg.create_cfg_item(_option, _workplace, _cookie, _owner, _description);
	UPDATE cfg.cfg_item SET value = _value WHERE pk = pk_item;
	return True;
end;';

comment on function cfg.set_option(IN _option text, IN _value anyelement, IN _workplace text, IN _cookie text, IN _owner text, IN _description text) is
	'set option, owner = empty means CURRENT_USER';

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-cfg-set_option.sql', 'v23');
