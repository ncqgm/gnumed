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
drop function if exists cfg.create_cfg_item(text, text, text, text, text) cascade;
drop function if exists cfg.set_option(text, anyelement, text, text, text) cascade;

-- --------------------------------------------------------------
drop function if exists cfg.set_option(IN _option text, IN _value jsonb, IN _workplace text, IN _cookie text, IN _owner text, IN _description text);


create function cfg.set_option(IN _option text, IN _value jsonb, IN _workplace text, IN _cookie text, IN _owner text, IN _description text)
	returns boolean
	language 'plpgsql'
	as '
DECLARE
	__pk_template integer;
	__pk_item integer;
BEGIN
	-- check template
	SELECT into __pk_template pk FROM cfg.cfg_template WHERE name = _option;
	if not FOUND then
		INSERT INTO cfg.cfg_template (name) VALUES (_option) RETURNING pk into __pk_template;
	end if;
	if _description is not NULL then
		UPDATE cfg.cfg_template
		SET description = _description
		WHERE pk = __pk_template;
	end if;
	-- check item
	if trim(_owner) = '''' then
		SELECT CURRENT_USER into _owner;
	end if;
	SELECT into __pk_item pk FROM cfg.cfg_item WHERE
		fk_template = __pk_template AND
		owner IS NOT DISTINCT FROM _owner AND
		workplace IS NOT DISTINCT FROM _workplace AND
		cookie IS NOT DISTINCT FROM _cookie;
	-- update item
	if FOUND then
		UPDATE cfg.cfg_item SET value = _value WHERE pk = __pk_item;
		return True;
	end if;

	-- newly create item
	INSERT INTO cfg.cfg_item (
		fk_template, workplace, cookie, owner, value
	) VALUES (
		__pk_template,
		_workplace,
		_cookie,
		_owner,
		_value
	);
	return True;
END;';


comment on function cfg.set_option(IN _option text, IN _value jsonb, IN _workplace text, IN _cookie text, IN _owner text, IN _description text) is
	'set option, owner = empty means CURRENT_USER';


revoke execute on function cfg.set_option(IN _option text, IN _value jsonb, IN _workplace text, IN _cookie text, IN _owner text, IN _description text) from public;
grant execute on function cfg.set_option(IN _option text, IN _value jsonb, IN _workplace text, IN _cookie text, IN _owner text, IN _description text) to "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-cfg-set_option.sql', 'v23');
