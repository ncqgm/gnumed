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
	id_person int references identity
);

CREATE TABLE m2m_staff_type (
	id_staff int references staff,
	id_enum_stafftype references enum_stafftype
);

CREATE TABLE m2m_staff_speciality (
	id_staff int references staff,
	id_speciality references enum_speciality
);

CREATE TABLE staff_working_hours (
	id_staff int references staff,
	dow int,
	from_time time,
	to_time time,
	as_staff int references enum_stafftype
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
	from time,
	to time
);

CREATE TABLE staff_working (
	id serial primary key,
	id_staff integer NOT NULL,
	date date,
	from time,
	to time,
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
	from time,
	to time,
	reason integer references enum_reason_for_absence,
	comment text
);

CREATE TABLE preferred_app_length (
	id serial primary key,
	id_staff integer,
	id_app_type integer references enum_app_types,
	duration integer  -- in minutes
);
