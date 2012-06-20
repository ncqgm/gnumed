-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;
--set check_function_bodies to on;

-- --------------------------------------------------------------
-- FIXME: rework gm.create_user()
SELECT gm.create_user('any-staff', 'any-staff');

REVOKE "gm-doctors" from "any-staff";
GRANT "gm-staff" TO "any-staff";

-- --------------------------------------------------------------
-- add identity
INSERT INTO dem.identity (
	gender,
	dob,
	cob,
	--deceased,
	title,
	tob,
	emergency_contact,
	comment
)	SELECT
		'f'::text,
		'1927-02-14'::timestamp with time zone,
		'CA'::text,
		-- '2007-09-29 13:30'::timestamp with time zone,
		'Lt.'::text,
		'12:30'::time without time zone,
		'James Bond'::text,
		'Queen and country, James.'::text
	WHERE NOT EXISTS (
		SELECT 1
		FROM dem.identity
		WHERE
			gender = 'f'
				AND
			dem.date_trunc_utc('day', dob) = '1927-02-14'::timestamp with time zone
	);

SELECT dem.add_name (
	(SELECT pk FROM dem.identity WHERE gender = 'f' AND dem.date_trunc_utc('day', dob) = '1927-02-14'::timestamp with time zone AND comment = 'Queen and country, James.'),
	'Jane',
	'Moneypenny',
	True
);

SELECT dem.add_name (
	(SELECT pk FROM dem.identity WHERE gender = 'f' AND dem.date_trunc_utc('day', dob) = '1927-02-14'::timestamp with time zone AND comment = 'Queen and country, James.'),
	'Lois Ruth',
	'Hooker',
	False
);

SELECT dem.add_name (
	(SELECT pk FROM dem.identity WHERE gender = 'f' AND dem.date_trunc_utc('day', dob) = '1927-02-14'::timestamp with time zone AND comment = 'Queen and country, James.'),
	'Lois',
	'Maxwell-Marriot',
	False
);

SELECT dem.set_nickname (
	(SELECT pk FROM dem.identity WHERE gender = 'f' AND dem.date_trunc_utc('day', dob) = '1927-02-14'::timestamp with time zone AND comment = 'Queen and country, James.'),
	'Penny'::text
);

-- turn into staff
INSERT INTO dem.staff (
	fk_identity,
	fk_role,
	db_user,
	short_alias,
	comment,
	is_active
)	SELECT
		(SELECT pk FROM dem.identity WHERE gender = 'f' AND dem.date_trunc_utc('day', dob) = '1927-02-14'::timestamp with time zone AND comment = 'Queen and country, James.'),
		(SELECT pk from dem.staff_role WHERE name = 'secretary'),
		'any-staff'::name,
		'MoPny'::text,
		'Secretary to the MI6 Chief, Second Officer of the Womens Royal Naval Service (Lieutnant of the Royal Navy)'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1
		FROM dem.staff
		WHERE
			db_user = 'any-staff'
	);

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-role-any_staff-create.sql', 'Revision: 1');
