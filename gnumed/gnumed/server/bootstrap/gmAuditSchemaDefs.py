"""Automatic GNUmed audit trail generation.

This module contains SQL DDL command templates for the audit
trail triggers and functions to be created in the schema "audit".

audit triggers are named "zt__SCHEMA__TABLE" to make
reasonably sure they are executed last.
"""
#==================================================================
__license__ = "GPL v2 or later"		# (details at https://www.gnu.org)

LOG_TABLE_PREFIX = 'log_'						# the audit trail tables start with this prefix
AUDIT_TRAIL_PARENT_TABLE = 'audit_trail'		# and inherit from this table
AUDIT_FIELDS_TABLE = 'audit_fields'				# audited tables inherit these fields
AUDIT_SCHEMA = 'audit'							# audit stuff lives in this schema

#==================================================================
# SQL statements for auditing setup script
#------------------------------------------------------------------
# ON INSERT
#------------------------------------------------------------------
SQL_TEMPLATE_INSERT_v23 = """-- old style
DROP FUNCTION IF EXISTS audit.ft_ins_%(src_tbl)s() cascade;

-- with schema
DROP FUNCTION IF EXISTS audit.ft_ins__%(src_schema)s__%(src_tbl)s() cascade;

CREATE FUNCTION audit.ft_ins__%(src_schema)s__%(src_tbl)s()
	RETURNS trigger
	LANGUAGE 'plpgsql'
	SECURITY DEFINER
	AS '
DECLARE
	_is_allowed_inserter boolean;
BEGIN
	-- is the session user allowed to insert data ?
	SELECT gm.account_is_dbowner_or_staff(SESSION_USER) INTO STRICT _is_allowed_inserter;
	IF _is_allowed_inserter IS FALSE THEN
		RAISE EXCEPTION
			''INSERT: gm.account_is_dbowner_or_staff(NAME): <%%> is neither database owner, nor <postgres>, nor on staff'', SESSION_USER
			USING ERRCODE = ''integrity_constraint_violation''
		;
		return NEW;
	END IF;
	NEW.row_version := 1;
	NEW.modified_when := CURRENT_TIMESTAMP;
	NEW.modified_by := SESSION_USER;
	return NEW;
END;';

CREATE TRIGGER zt_ins__%(src_schema)s__%(src_tbl)s
	BEFORE INSERT ON %(src_schema)s.%(src_tbl)s
	FOR EACH ROW EXECUTE PROCEDURE audit.ft_ins__%(src_schema)s__%(src_tbl)s();
"""

# v21, v22: gm.account_is_dbowner_or_staff() exists but schema not yet renamed
SQL_TEMPLATE_INSERT_v21 = """DROP FUNCTION IF EXISTS audit.ft_ins_%(src_tbl)s() cascade;

CREATE FUNCTION audit.ft_ins_%(src_tbl)s()
	RETURNS trigger
	LANGUAGE 'plpgsql'
	SECURITY DEFINER
	AS '
DECLARE
	_is_allowed_inserter boolean;
BEGIN
	-- is the session user allowed to insert data ?
	SELECT gm.account_is_dbowner_or_staff(SESSION_USER) INTO STRICT _is_allowed_inserter;
	IF _is_allowed_inserter IS FALSE THEN
		RAISE EXCEPTION
			''INSERT: gm.account_is_dbowner_or_staff(NAME): <%%> is neither database owner, nor <postgres>, nor on staff'', SESSION_USER
			USING ERRCODE = ''integrity_constraint_violation''
		;
		return NEW;
	END IF;
	NEW.row_version := 0;				-- changes in v23
	NEW.modified_when := CURRENT_TIMESTAMP;
	NEW.modified_by := SESSION_USER;
	return NEW;
END;';

CREATE TRIGGER zt_ins_%(src_tbl)s
	BEFORE INSERT ON %(src_schema)s.%(src_tbl)s
	FOR EACH ROW EXECUTE PROCEDURE audit.ft_ins_%(src_tbl)s();
"""

# pre-v21, because no gm.account_is_dbowner_or_staff()
SQL_TEMPLATE_INSERT_NO_INSERTER_CHECK = """DROP FUNCTION IF EXISTS audit.ft_ins_%(src_tbl)s() cascade;

CREATE FUNCTION audit.ft_ins_%(src_tbl)s()
	RETURNS trigger
	LANGUAGE 'plpgsql'
	SECURITY DEFINER
	AS '
BEGIN
	NEW.row_version := 0;				-- changes in v23
	NEW.modified_when := CURRENT_TIMESTAMP;
	NEW.modified_by := SESSION_USER;
	return NEW;
END;';

CREATE TRIGGER zt_ins_%(src_tbl)s
	BEFORE INSERT ON %(src_schema)s.%(src_tbl)s
	FOR EACH ROW EXECUTE PROCEDURE audit.ft_ins_%(src_tbl)s();
"""

#------------------------------------------------------------------
# ON UPDATE
#------------------------------------------------------------------
SQL_TEMPLATE_UPDATE_v23 = """-- old style
DROP FUNCTION IF EXISTS audit.ft_upd_%(src_tbl)s() cascade;

-- with schema
DROP FUNCTION IF EXISTS audit.ft_upd__%(src_schema)s__%(src_tbl)s() cascade;

CREATE FUNCTION audit.ft_upd__%(src_schema)s__%(src_tbl)s()
	RETURNS trigger
	LANGUAGE 'plpgsql'
	SECURITY DEFINER
	AS '
DECLARE
	_is_allowed_updater boolean;
BEGIN
	-- is the session user allowed to update data ?
	SELECT gm.account_is_dbowner_or_staff(SESSION_USER) INTO STRICT _is_allowed_updater;
	IF _is_allowed_updater IS FALSE THEN
		RAISE EXCEPTION
			''UPDATE: gm.account_is_dbowner_or_staff(NAME): <%%> is neither database owner, nor <postgres>, nor on staff'', SESSION_USER
			USING ERRCODE = ''integrity_constraint_violation''
		;
		return NEW;
	END IF;
	-- stash away OLD row before UPDATE
	INSERT INTO audit.%(log_tbl)s (
		row_version, version_created_when, version_created_by, src_row_pk_audit, src_table_oid, version_logged_why,
		%(cols_clause)s
	) VALUES (
		OLD.row_version, OLD.modified_when, OLD.modified_by, OLD.pk_audit, TG_RELID, TG_OP,
		%(vals_clause)s
	);
	NEW.row_version := OLD.row_version + 1;
	NEW.modified_when := CURRENT_TIMESTAMP;
	NEW.modified_by := SESSION_USER;
	return NEW;
END;';

CREATE TRIGGER zt_upd__%(src_schema)s__%(src_tbl)s
	BEFORE UPDATE ON %(src_schema)s.%(src_tbl)s
	FOR EACH ROW EXECUTE PROCEDURE audit.ft_upd__%(src_schema)s__%(src_tbl)s();
"""

# v21 / v22
SQL_TEMPLATE_UPDATE_v21 = """DROP FUNCTION IF EXISTS audit.ft_upd_%(src_tbl)s() cascade;

CREATE FUNCTION audit.ft_upd_%(src_tbl)s()
	RETURNS trigger
	LANGUAGE 'plpgsql'
	SECURITY DEFINER
	AS '
DECLARE
	_is_allowed_updater boolean;
BEGIN
	-- is the session user allowed to update data ?
	SELECT gm.account_is_dbowner_or_staff(SESSION_USER) INTO STRICT _is_allowed_updater;
	IF _is_allowed_updater IS FALSE THEN
		RAISE EXCEPTION
			''UPDATE: gm.account_is_dbowner_or_staff(NAME): <%%> is neither database owner, nor <postgres>, nor on staff'', SESSION_USER
			USING ERRCODE = ''integrity_constraint_violation''
		;
		return NEW;
	END IF;
	-- stash away OLD row before UPDATE
	INSERT INTO audit.%(log_tbl)s (
		orig_version, orig_when, orig_by, orig_tableoid, audit_action,
		%(cols_clause)s
	) VALUES (
		OLD.row_version, OLD.modified_when, OLD.modified_by, TG_RELID, TG_OP,
		%(vals_clause)s
	);
	NEW.row_version := OLD.row_version + 1;
	NEW.modified_when := CURRENT_TIMESTAMP;
	NEW.modified_by := SESSION_USER;
	return NEW;
END;';

CREATE TRIGGER zt_upd_%(src_tbl)s
	BEFORE UPDATE ON %(src_schema)s.%(src_tbl)s
	FOR EACH ROW EXECUTE PROCEDURE audit.ft_upd_%(src_tbl)s();
"""

# pre-v21, because no gm.account_is_dbowner_or_staff()
SQL_TEMPLATE_UPDATE_NO_UPDATER_CHECK = """DROP FUNCTION IF EXISTS audit.ft_upd_%(src_tbl)s() cascade;

CREATE FUNCTION audit.ft_upd_%(src_tbl)s()
	RETURNS trigger
	LANGUAGE 'plpgsql'
	SECURITY DEFINER
	AS '
BEGIN
	NEW.row_version := OLD.row_version + 1;
	NEW.modified_when := CURRENT_TIMESTAMP;
	NEW.modified_by := SESSION_USER;
	INSERT INTO audit.%(log_tbl)s (
		orig_version, orig_when, orig_by, orig_tableoid, audit_action,
		%(cols_clause)s
	) VALUES (
		OLD.row_version, OLD.modified_when, OLD.modified_by, TG_RELID, TG_OP,
		%(vals_clause)s
	);
	return NEW;
END;';

CREATE TRIGGER zt_upd_%(src_tbl)s
	BEFORE UPDATE ON %(src_schema)s.%(src_tbl)s
	FOR EACH ROW EXECUTE PROCEDURE audit.ft_upd_%(src_tbl)s();
"""

#------------------------------------------------------------------
# ON DELETE
#------------------------------------------------------------------
SQL_TEMPLATE_DELETE_v23 = """-- old style
DROP FUNCTION IF EXISTS audit.ft_del_%(src_tbl)s() cascade;

-- with schema
DROP FUNCTION IF EXISTS audit.ft_del__%(src_schema)s__%(src_tbl)s() cascade;

CREATE FUNCTION audit.ft_del__%(src_schema)s__%(src_tbl)s()
	RETURNS trigger
	LANGUAGE 'plpgsql'
	SECURITY DEFINER
	AS '
DECLARE
	_is_allowed_deleter boolean;
BEGIN
	-- is the session user allowed to delete data ?
	SELECT gm.account_is_dbowner_or_staff(SESSION_USER) INTO STRICT _is_allowed_deleter;
	IF _is_allowed_deleter IS FALSE THEN
		RAISE EXCEPTION
			''DELETE: gm.account_is_dbowner_or_staff(NAME): <%%> is neither database owner, nor <postgres>, nor on staff'', SESSION_USER
			USING ERRCODE = ''integrity_constraint_violation''
		;
		return OLD;
	END IF;
	-- stash away OLD row before DELETE
	INSERT INTO audit.%(log_tbl)s (
		row_version, version_created_when, version_created_by, src_row_pk_audit, src_table_oid, version_logged_why,
		%(cols_clause)s
	) VALUES (
		OLD.row_version, OLD.modified_when, OLD.modified_by, OLD.pk_audit, TG_RELID, TG_OP,
		%(vals_clause)s
	);
	return OLD;
END;';

CREATE TRIGGER zt_del__%(src_schema)s__%(src_tbl)s
	BEFORE DELETE ON %(src_schema)s.%(src_tbl)s
	FOR EACH ROW EXECUTE PROCEDURE audit.ft_del__%(src_schema)s__%(src_tbl)s();
"""

# v21 / v22
SQL_TEMPLATE_DELETE_v21 = """DROP FUNCTION IF EXISTS audit.ft_del_%(src_tbl)s() cascade;

CREATE FUNCTION audit.ft_del_%(src_tbl)s()
	RETURNS trigger
	LANGUAGE 'plpgsql'
	SECURITY DEFINER
	AS '
DECLARE
	_is_allowed_deleter boolean;
BEGIN
	-- is the session user allowed to delete data ?
	SELECT gm.account_is_dbowner_or_staff(SESSION_USER) INTO STRICT _is_allowed_deleter;
	IF _is_allowed_deleter IS FALSE THEN
		RAISE EXCEPTION
			''DELETE: gm.account_is_dbowner_or_staff(NAME): <%%> is neither database owner, nor <postgres>, nor on staff'', SESSION_USER
			USING ERRCODE = ''integrity_constraint_violation''
		;
		return OLD;
	END IF;
	-- stash away OLD row before DELETE
	INSERT INTO audit.%(log_tbl)s (
		orig_version, orig_when, orig_by, orig_tableoid, audit_action,
		%(cols_clause)s
	) VALUES (
		OLD.row_version, OLD.modified_when, OLD.modified_by, TG_RELID, TG_OP,
		%(vals_clause)s
	);
	return OLD;
END;';

CREATE TRIGGER zt_del_%(src_tbl)s
	BEFORE DELETE ON %(src_schema)s.%(src_tbl)s
	FOR EACH ROW EXECUTE PROCEDURE audit.ft_del_%(src_tbl)s();
"""

# pre-v21, because no gm.account_is_dbowner_or_staff()
SQL_TEMPLATE_DELETE_NO_DELETER_CHECK = """DROP FUNCTION IF EXISTS audit.ft_del_%(src_tbl)s() cascade;

CREATE FUNCTION audit.ft_del_%(src_tbl)s()
	RETURNS trigger
	LANGUAGE 'plpgsql'
	SECURITY DEFINER
	AS '
BEGIN
	INSERT INTO audit.%(log_tbl)s (
		orig_version, orig_when, orig_by, orig_tableoid, audit_action,
		%(cols_clause)s
	) VALUES (
		OLD.row_version, OLD.modified_when, OLD.modified_by, TG_RELID, TG_OP,
		%(vals_clause)s
	);
	return OLD;
END;';

CREATE TRIGGER zt_del_%(src_tbl)s
	BEFORE DELETE ON %(src_schema)s.%(src_tbl)s
	FOR EACH ROW EXECUTE PROCEDURE audit.ft_del_%(src_tbl)s();
"""

SQL_TEMPLATE_CREATE_AUDIT_TRAIL_TABLE = """
create table %(log_schema)s.%(log_tbl)s (
	%(log_cols)s
) inherits (%(log_schema)s.%(log_base_tbl)s);
"""

SQL_TEMPLATE__index__pk_audit__row_version = """
drop index if exists audit.idx_uniq__audit__%(log_tbl)s__pk_audit_per_row_ver cascade;

create unique index idx_uniq__audit__%(log_tbl)s__pk_audit_per_row_ver
       on audit.%(log_tbl)s(src_row_pk_audit, row_version);
"""

#==================================================================
# main
#------------------------------------------------------------------
if __name__ == "__main__" :
	pass
