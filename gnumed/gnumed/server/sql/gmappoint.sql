-- suggested server ER script for clinic appointments
-- 29/10/01 Ian Haywood
-- Interface needs to be written.
-- PHP interface for Web: good idea?

-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================


CREATE TABLE enum_stafftype (
	id serial primary key,
	description varchar(30)
);

INSERT INTO enum_stafftype(description) VALUES ('doctor');
INSERT INTO enum_stafftype(description) VALUES ('doctor (locum)');
INSERT INTO enum_stafftype(description) VALUES ('nurse');
INSERT INTO enum_stafftype(description) VALUES ('receptionist');
INSERT INTO enum_stafftype(description) VALUES ('office');

CREATE TABLE enum_speciality (
	id serial primary key,
	description varchar(30)
);

INSERT INTO enum_speciality(description) VALUES ('General Practice');
INSERT INTO enum_speciality(description) VALUES ('General Practice (VR)');
INSERT INTO enum_speciality(description) VALUES ('General Practice (ROMPS)');
INSERT INTO enum_speciality(description) VALUES ('General Surgery');
INSERT INTO enum_speciality(description) VALUES ('Obstetrics GP');
INSERT INTO enum_speciality(description) VALUES ('Obstetrics & Gynaecology');
INSERT INTO enum_speciality(description) VALUES ('Anaesthesist GP');
INSERT INTO enum_speciality(description) VALUES ('Anaesthesist Specialist');

CREATE TABLE staff (
	id serial primary key,
	--id_person int references identity
	-- provisional, to make appointments work right now:
	surnames varchar(60),
	givennames varchar(60),
	title varchar(12),
	qualifications varchar(254)
);

CREATE TABLE m2m_staff_type (
	id_staff integer references staff,
	id_enum_stafftype integer references enum_stafftype
);

CREATE TABLE m2m_staff_speciality (
	id_staff integer references staff,
	id_speciality integer references enum_speciality
);

CREATE TABLE location
       (
		id SERIAL,
		name varchar (50)
	);

--=====================================================================

CREATE TABLE session (
		clinician INTEGER NOT NULL REFERENCES staff (id),
		start TIME NOT NULL,
		finish TIME NOT NULL,
		day INT2 NOT NULL, 
		comment TEXT, 
		location INTEGER REFERENCES location (id),
		id SERIAL
	);

COMMENT ON TABLE session IS 
'All sessions of all doctors in the clinic';
COMMENT ON COLUMN session.start IS 
'Time the session starts (the first appointment)';
COMMENT ON COLUMN session.finish IS 
'Time the session finishes (no appointments after this)';
COMMENT ON COLUMN session.day IS 
'Day of the week on which the clinic is held, 0=Sunday, 1=Monday, etc.';



CREATE public_holiday 
       (
		day DATE
	);

COMMENT ON TABLE holiday IS 'public holiday. Can be pre-loaded with standrad
public holidays for the next n years.';

--===================================================================


CREATE TABLE enum_app_type (
	id serial primary key,
	description text
);

INSERT INTO enum_app_type(description) VALUES ('standard');
INSERT INTO enum_app_type(description) VALUES ('short');
INSERT INTO enum_app_type(description) VALUES ('long');
INSERT INTO enum_app_type(description) VALUES ('check-up geriatric');
INSERT INTO enum_app_type(description) VALUES ('medication review');
INSERT INTO enum_app_type(description) VALUES ('psychiatric');
INSERT INTO enum_app_type(description) VALUES ('substance abuse - first');
INSERT INTO enum_app_type(description) VALUES ('family');
INSERT INTO enum_app_type(description) VALUES ('partner therapy');
INSERT INTO enum_app_type(description) VALUES ('group therapy');


CREATE TABLE preferred_app_length (
	id serial primary key,
	id_staff integer references staff (id),
	id_enum_app_type integer references enum_app_type,
	duration INTERVAL
);

--=======================================================================

CREATE TABLE appointment
       (
		session INTEGER REFERENCES session (id),
		patient INTEGER,
		patient_name varchar (100),
		type INTEGER REFERENCES enum_app_type (id),
		date TIMESTAMP
	);

CREATE TABLE meeting 
       (
		id SERIAL,
		topic varchar (100),
		document TEXT,
		time TIMESTAMP,
		duration INTERVAL,
		location REFERENCES location (id),
	);

COMMENT ON TABLE meeting IS 'Meetings held at clinic/hospital/etc.';
COMMENT ON COLUMN meeting.document IS 'AbiWord file for discussion
document';

CREATE TABLE meeting_attendance 
       (
		staff INTEGER REFERENCES staff (id),
		meeting INTEGER REFERENCES meeting (id),
		confirmed BOOL
	);

COMMENT ON TABLE meeting_attendance IS 'links people to meetings.
INSERTing into this table does not guarantee their attendance.';

CREATE TABLE other_event 
       (
		staff INTEGER staff (id),
		event varchar (100),
		date TIMESTAMP,
		duration INTERVAL,
		personal BOOL
	) INHERITS (event);

COMMENT ON TABLE other_event IS 'Everything that is not seeing a patient or a meeting with other staff (i.e a general dairy entry), including leave of absence (set duration to days, weeks, etc.';

COMMENT ON COLUMN other_event.personal IS 'Only readable by owner (enforced by clients. Paranoid should use cryptowidget';

--=======================================================================

CREATE TABLE event_types
       (
		id SERIAL,
		name varchar (50)
	);

insert into event_types (id, name) values (1, 'patient');
insert into event_types (id, name) values (2, 'meeting');
insert into event_types (id, name) values (3, 'other'):


--Now link all 3 types of event into a single view

CREATE VIEW v_event AS 
SELECT 3 AS type, staff, event AS text, date, duration FROM other_event
       UNION
SELECT 2 AS type, meeting_attendance.staff AS staff, meeting.topic AS text, meeting.date AS date, meeting.duration AS duration FROM meeting, meeting_attendance WHERE meeting_attendance.meeting = meeting.id;
       UNION
SELECT 1 AS type, session.clinician AS staff, appointment.patient_name AS text, appointment.date AS date,
preferred_app_length.duration FROM session, appointment, preferred_app_length WHERE appointment.session = session.id AND appointment.type = preferred_app_length.id_enum_app_type AND session.clinician = preferred_app_length.id_staff;      

--==========================================================

-- a function to get the first available appointment for any staff
CREATE FUNCTION get_first_avail (INTEGER, DATE, INTERVAL)
RETURNS TIMESTAMP AS '
DECLARE
	clinician ALIAS FOR $1;
	start ALIAS FOR $2;
	day FLOAT8;
	avail_epoch INTEGER; -- time as UNIX type
	start_epoch INTEGER;
	avail_date DATE;
	avail_time TIME;
	dummy RECORD; -- PL/SQL allows SELECT..INTO but not select.
BEGIN
	SELECT * INTO dummy FROM session WHERE session.clinician = clinician;
	IF NOT FOUND THEN
	   RAISE EXCEPTION ''clinician has no session'';
	   -- check sessions listed, (otherwise infinite loop!)
	END IF;
	start_epoch = extract (epoch from start); -- convert to UNIX time (SQL
	-- time cannot be incremented without weird bugs)
	avail_epoch := start_epoch; 
	day := extract (dow from start); -- find day of week.
	LOOP
		avail_date := date (avail_epoch); -- convert to SQL time
		SELECT min (list.time) INTO avail_time FROM list, session WHERE
		       session.clinician = clinician AND -- doctor''s sessions
		       float8 (session.day) = day AND -- right day of week
		       list.session = session.id AND -- slots of session
		       isfree (session.id, avail_date, list.time) AND -- check is free
		       isnotonholiday (clinician, avail_date, list.time) AND -- check not on holiday
		       timestamp (avail_date, list.time) > now (); -- must not be before now (), free appts past are unless.
		IF NOT avail_time ISNULL THEN -- appt found!
		   RETURN timestamp (avail_date, avail_time);
		END IF;
		day := day + 1.0; -- next day of week
		IF day = 7.0 THEN
		   day := 0.0;
		END IF;
		avail_epoch := avail_epoch + 86400; -- (one day in seconds) increment day.
		IF avail_epoch - start_epoch > 315360000 THEN -- 10 years 
		   -- in seconds. Prevents infinite loops. 
		   RAISE EXCEPTION ''10 years into the future: stop'';
		END IF;
	END LOOP;
END;' LANGUAGE 'plpgsql';

COMMENT ON FUNCTION get_first_avail (integer, date) IS
'Starting at date, the function searches forward through time until
a time is found available for an appointment.
WARNING: potentially very slow.';

CREATE VIEW first_available AS SELECT name, get_first_avail (id, date (now ())) FROM clinician; 

COMMENT ON VIEW first_available IS
'Convience view for a list of all doctors and when they are available.
WARNING: Queries on this table may be VERY SLOW.';
