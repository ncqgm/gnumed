-- halt on any error
\SET ON_ERROR_STOP

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

CREATE TABLE staff_working_hours (
	id_staff integer references staff,
	dow integer,
	from_time time,
	to_time time,
	as_staff integer references enum_stafftype
);


CREATE TABLE public_holidays (
	id serial primary key,
	date_from date,
	date_to date,
	name varchar(30),
	valid_in text
);

CREATE TABLE surgery_open (
	id_surgery integer,		-- should reference f.k.
	date date,
	from_t time,
	to_t time
);

CREATE TABLE staff_working (
	id serial primary key,
	id_staff integer NOT NULL,
	date date,
	from_t time,
	to_t time
);

CREATE TABLE enum_absence_reason (
	id serial primary key,
	description varchar(20)
);

INSERT INTO enum_absence_reason(description) VALUES('unexplained');
INSERT INTO enum_absence_reason(description) VALUES('late');
INSERT INTO enum_absence_reason(description) VALUES('illness');
INSERT INTO enum_absence_reason(description) VALUES('death');
INSERT INTO enum_absence_reason(description) VALUES('holiday');
INSERT INTO enum_absence_reason(description) VALUES('family');
INSERT INTO enum_absence_reason(description) VALUES('other');


CREATE TABLE staff_absent (
	id serial primary key,
	id_staff integer NOT NULL,
	date date,
	from_t time,
	to_t time,
	reason integer references enum_absence_reason,
	comment text
);

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
	id_staff integer,
	id_enum_app_type integer references enum_app_type,
	duration integer  -- in minutes
);

create table days_off(
	id serial primary key, 
	id_staff integer references staff, 
	day_of_week integer default 6 -- day of week, Monday=0, Sunday=6
);


CREATE VIEW v_doctors_only AS
	select * from staff where id =
	(select id_staff from m2m_staff_type where id_enum_stafftype=
	(select id from enum_stafftype where description='doctor'));

CREATE VIEW v_duration_standard AS
	select duration, id_staff  from preferred_app_length
	where id_enum_app_type =
	(select id from enum_app_type where description='standard');

CREATE VIEW v_duration_long AS
	select duration, id_staff from preferred_app_length
	where id_enum_app_type =
	(select id from enum_app_type where description='long');

CREATE VIEW v_duration_short AS
	select duration, id_staff from preferred_app_length
	where id_enum_app_type =
	(select id from enum_app_type where description='short');


