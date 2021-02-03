-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

set check_function_bodies to on;

-- --------------------------------------------------------------
delete from audit.audited_tables where
	schema = 'dem'
		and
	table_name = 'lnk_identity2primary_doc';

-- --------------------------------------------------------------
create or replace function dem.remove_person(integer)
	returns boolean
	language 'plpgsql'
	security invoker
	as '
DECLARE
	_pk_identity alias for $1;
BEGIN
	-- does person exist ?
	perform 1 from dem.identity where pk = _pk_identity;
	if not FOUND then
		raise notice ''dem.remove_person(): dem.identity.pk=(%) does not exist, not removing'', _pk_identity;
		return false;
	end if;

	-- we cannot just get the child tables of clin.clin_root_item and
	-- delete from them since they are inter-dependent and may require
	-- a particular order of deletion, so let us do that explicitly:
	DELETE FROM clin.clin_hx_family WHERE fk_encounter IN (
		select pk from clin.encounter where fk_patient = _pk_identity
	);
	DELETE FROM clin.vaccination WHERE fk_encounter IN (
		select pk from clin.encounter where fk_patient = _pk_identity
	);
	DELETE FROM clin.allergy WHERE fk_encounter IN (
		select pk from clin.encounter where fk_patient = _pk_identity
	);
	DELETE FROM clin.allergy_state WHERE fk_encounter IN (
		select pk from clin.encounter where fk_patient = _pk_identity
	);
	DELETE FROM clin.clin_diag WHERE fk_narrative IN (
		SELECT pk FROM clin.clin_narrative WHERE fk_encounter IN (
			select pk from clin.encounter where fk_patient = _pk_identity
		)
	);
	DELETE FROM clin.test_result WHERE fk_encounter IN (
		select pk from clin.encounter where fk_patient = _pk_identity
	);
	DELETE FROM clin.lab_request WHERE fk_encounter in (
		select pk from clin.encounter where fk_patient = _pk_identity
	);
	DELETE FROM clin.substance_intake WHERE fk_encounter IN (
		select pk from clin.encounter where fk_patient = _pk_identity
	);
	DELETE FROM clin.procedure WHERE fk_encounter IN (
		select pk from clin.encounter where fk_patient = _pk_identity
	);
	DELETE FROM clin.clin_narrative WHERE fk_encounter IN (
		select pk from clin.encounter where fk_patient = _pk_identity
	);
	DELETE FROM blobs.doc_med WHERE fk_encounter IN (
		select pk from clin.encounter where fk_patient = _pk_identity
	);

	-- now that we have deleted all the clinical data let us
	-- delete the EMR structural items as well:
	DELETE FROM clin.episode WHERE fk_encounter IN (
	    select pk from clin.encounter where fk_patient = _pk_identity
	);
	DELETE FROM clin.health_issue WHERE fk_encounter IN (
	    select pk from clin.encounter where fk_patient = _pk_identity
	);
	DELETE FROM clin.encounter WHERE fk_patient = _pk_identity;

	-- delete demographics details:
	DELETE FROM dem.identity_tag where fk_identity = _pk_identity;
	DELETE FROM dem.names WHERE id_identity = _pk_identity;

	-- eventually delete the identity itself which does
	-- not go down without some twisting of arms:
	ALTER TABLE dem.identity disable rule r_del_identity;
	DELETE FROM dem.identity WHERE pk = _pk_identity;
	ALTER TABLE dem.identity enable rule r_del_identity;

	return true;
END;';


comment on function dem.remove_person(integer) is
'Fully remove a person from the system - except
 everything is still in the audit tables ;-)';

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-dem-f_remove_person.sql', 'Revision 1');

-- ==============================================================
