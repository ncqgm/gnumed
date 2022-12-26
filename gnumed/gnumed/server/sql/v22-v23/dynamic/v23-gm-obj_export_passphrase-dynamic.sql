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
comment on table gm.obj_export_passphrase is
'Stores passphrases used when exporting objects for distribution.
.
The passphrase used for encrypting the exported object is
itself encrypted with the public key of the exporting user
and the admin user.
.
Can be used to recover data externally later on as follows:
.
External provider asks for password for a given file.
.
External provider is asked to create hashes for the file using
each algorithm that is found in .hash_type in this database.
.
Local provider searches for the created hash in this database.
.
If hash is found, local provider uses the secret key of
either the exporter or the admin to retrieve the password.
';

revoke all on gm.obj_export_passphrase from public ;
grant insert, update on gm.obj_export_passphrase to "gm-staff";
grant delete on gm.obj_export_passphrase to "gm-dbo";

-- --------------------------------------------------------------
comment on column gm.obj_export_passphrase.hash_type is
	'The algorithm used for creating the .hash of the exported object, say, "SHA256", "MD5", ...';

alter table gm.obj_export_passphrase
	alter column hash_type
		set default null;

alter table gm.obj_export_passphrase
	alter column hash_type
		set not null;

-- --------------------------------------------------------------
comment on column gm.obj_export_passphrase.hash is
	'The actual hash of the exported object.';

alter table gm.obj_export_passphrase
	alter column hash
		set default null;

alter table gm.obj_export_passphrase
	alter column hash
		set not null;

-- --------------------------------------------------------------
comment on column gm.obj_export_passphrase.phrase is
	'The (encrypted) passphrase used to encrypt the exported object.';

alter table gm.obj_export_passphrase
	alter column phrase
		set default null;

alter table gm.obj_export_passphrase
	alter column phrase
		set not null;

-- --------------------------------------------------------------
comment on column gm.obj_export_passphrase.description is 
'Structured information guiding the user in more quickly
identifying the encrypted external object.
.
Could be a filename, a recipient, ...
';

alter table gm.obj_export_passphrase
	alter column description
		set default null;

-- --------------------------------------------------------------
drop index if exists gm.idx_uniq_obj_exp_passphrase_row cascade;
create unique index idx_uniq_obj_exp_passphrase_row on gm.obj_export_passphrase(hash_type, hash, phrase);

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-gm-obj_export_passphrase-dynamic.sql', '23.0');
