-- suggested server ER script for clinic appointments
-- 29/10/01 Ian Haywood
-- Interface needs to be written.
-- PHP interface for Web: good idea?


CREATE TABLE clinician -- temporary ??
	(
		name TEXT NOT NULL,
		bio TEXT,
		photo TEXT, -- JPEG
		id SERIAL 
	);

COMMENT ON TABLE clinician IS 'Table of all clinicians';
COMMENT ON COLUMN clinician.name IS 'Full name';
COMMENT ON COLUMN clinician.bio IS 'Short CV for display on Website, in HTML';
COMMENT ON COLUMN clinician.photo IS 'Photograph as JPEG';

CREATE TABLE session (
		clinician INTEGER NOT NULL REFERENCES clinician (id),
		start TIME NOT NULL,
		finish TIME NOT NULL,
		day INT2 NOT NULL, 
		consult_time INTERVAL NOT NULL, 
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
COMMENT ON COLUMN session.consult_time IS 
'The spacing of the appointments';

CREATE TABLE holiday
	(
		clinician INTEGER NOT NULL REFERENCES clinician (id),
		start TIMESTAMP NOT NULL,
		finish TIMESTAMP NOT NULL
	);

COMMENT ON TABLE holiday IS 
'Details of holidays about to be taken. Should be used even for short time, 
i.e. an afernoon off';
COMMENT ON COLUMN holiday.start IS 
'Date and time from which appointments are not accepted';
COMMENT ON COLUMN holiday.finish IS 
'Date and time from which appointments can be booked';


CREATE TABLE appointment
	(
		patient_name varchar(50) NOT NULL,
		session INTEGER NOT NULL REFERENCES session (id),
		time TIMESTAMP NOT NULL, -- date and time of appointment
		length INT2 NOT NULL, -- 1=single, 2=double, etc. 0=fake entry for extended consults
		booked TIMESTAMP NOT NULL,
		patient_ur INTEGER -- what type should this be???
	); 

COMMENT ON TABLE appointment IS 'All appointments made';
COMMENT ON COLUMN appointment.patient_name IS 
'Name of patient as surname,, first name. For speed so don''t have to query
patient server all the time.';
COMMENT ON COLUMN appointment.session IS 
'ID of session under which pt is booked';
COMMENT ON COLUMN appointment.time IS 'date/time of booking';
COMMENT ON COLUMN appointment.length IS 
'length of booking 1=normal booking, 2=double-length consult,, 0=dummy entry 
for a previous double consult.';
COMMENT ON COLUMN appointment.booked IS 
'Time booking was made. Set by trigger';
COMMENT ON COLUMN appointment.patient_ur IS 
'UR code, reference to central patient table. What should the type be??. Can be NULL 
for new patients';

CREATE TABLE list
	(
		time TIME,
		session INTEGER REFERENCES session (id)
	);

COMMENT ON TABLE list IS 
'Auto-generated list, with one entry for each ''slot'' available in the 
doctor''s timetable.';
COMMENT ON COLUMN list.time IS 'Time during the day of consult.';
COMMENT ON COLUMN list.session IS 'ID of session referred to';

CREATE FUNCTION list_create () RETURNS OPAQUE AS '
DECLARE
	curr TIME;
BEGIN
	IF TG_OP = ''DELETE'' OR TG_OP = ''UPDATE'' THEN
	-- delete entries in list.
	   DELETE FROM list WHERE list.session = OLD.id;
	END IF;
	IF TG_OP = ''INSERT'' OR TG_OP = ''UPDATE'' THEN
	   curr := NEW.start;    
	   WHILE curr < NEW.finish LOOP
		 INSERT INTO list VALUES (curr, NEW.id);
		 curr := curr + NEW.consult_time;
	   END LOOP;
	   RETURN NEW;
	END IF;
	RETURN NULL;
END;
' LANGUAGE 'plpgsql';

CREATE TRIGGER list_create AFTER INSERT OR UPDATE OR DELETE 
       ON session FOR EACH ROW EXECUTE PROCEDURE list_create ();

COMMENT ON TRIGGER list_create ON session IS
'When a session is created, entries are inserted into table list for each 
appointment slot in that session. If the session is deleted or updated, the 
previous entries in list are removed';

CREATE FUNCTION new_appointment () RETURNS OPAQUE AS '
DECLARE
	double_time TIMESTAMP;
	consult_length INTERVAL;
	dummy RECORD;
BEGIN
	IF TG_OP = ''DELETE'' OR TG_OP = ''UPDATE'' THEN
	   IF OLD.length > 1 THEN
	      double_time:=OLD.time; -- delete all the extras on this appt
	      SELECT consult_time INTO consult_length FROM session
	      WHERE session.id = OLD.session; 
	      FOR i IN 2..OLD.length LOOP
	      -- go through and delete the extras for double appt.
		  double_time := double_time + consult_length;
		  -- this will recur, but that''s OK. Note length=0
		  DELETE FROM appointment
			 WHERE patient_name = OLD.patient_name 
			 AND session = OLD.session 
			 AND time = double_time
			 AND length = 0
			AND (patient_ur ISNULL OR patient_ur = OLD.patient_ur);
	      END LOOP;
	   END IF;  
	END IF; 
	IF TG_OP = ''INSERT'' OR TG_OP = ''UPDATE'' THEN 
	   -- check not double-booked.
	   SELECT * INTO dummy FROM appointment WHERE 
	       session = NEW.session AND
	       time = NEW.time;
	   IF FOUND THEN
		 RAISE EXCEPTION ''Double booked'';
	   END IF; 
	   -- make sure appointment actually exists
	   SELECT * INTO dummy FROM list WHERE
	       list.session = NEW.session AND
	       list.time = time (NEW.time);
	   IF NOT FOUND THEN
	      RAISE EXCEPTION ''No such time'';
	   END IF; 
	   -- check not on holiday
	   SELECT * INTO dummy FROM holiday, session WHERE
	       holiday.clinician = session.clinician
	       AND session.id = NEW.session
	       AND holiday.start < NEW.time 
	       AND holiday.finish > NEW.time;
	   IF FOUND THEN
	      RAISE EXCEPTION ''Doctor on holiday'';
	   END IF; 
	   -- add doubles in appointment book
	   IF NEW.length > 1 THEN
	      SELECT consult_time INTO consult_length FROM session
	      WHERE session.id = NEW.session;
	      double_time := NEW.time;
	      FOR i IN 2..NEW.length LOOP
		  double_time := double_time + consult_length;
		  -- this will recur, but that''s OK. Note length=0
		  INSERT INTO appointment VALUES (NEW.patient_name, 
			 NEW.session, double_time, 0);
	      END LOOP;
	   END IF;
	   NEW.booked := now (); -- mark booking time 
	   RETURN NEW;
	END IF;
	RETURN OLD; -- only get here if TG_OP = ''DELETE''
END;
' LANGUAGE 'plpgsql';

CREATE TRIGGER new_appointment BEFORE INSERT OR UPDATE OR DELETE ON appointment
FOR EACH ROW EXECUTE PROCEDURE new_appointment (); 

COMMENT ON TRIGGER new_appointment ON appointment IS
'Checks all new appointments, to make sure they don''t clash with holidays
or other appointments, and that the doctor is in at that time.
If the appointment is a multiple, dummy entries are inserted, with length=0
at later times to prevent bookings in these times.
If an appointment is deleted, the dummies are deleted.
A timestamp is added of when the booking is made.';

-- Function to get if a time is booked. True if booked, false if not booked,
-- NULL of no time available.
-- First param is doctors ID.

CREATE FUNCTION is_booked (INTEGER, DATE, TIME)
RETURNS BOOLEAN AS '
DECLARE
	clinician ALIAS FOR $1;
	appt_date ALIAS FOR $2;
	appt_time ALIAS FOR $3;
	appt datetime;
	dummy RECORD; -- SELECTs *must be* "SELECT INTO" even if we don''t care about the result. 
BEGIN
	appt := timestamp (appt_date, appt_time);
	-- find if booked to other patient
	SELECT * INTO dummy FROM appointment, session
	WHERE appointment.time = appt AND
	      appointment.session = session.id AND
	      session.clinician = clinician;
	IF FOUND THEN
	   RETURN ''t'';
	END IF;
	-- check not on holiday
	SELECT * INTO dummy FROM holiday WHERE
	       holiday.clinician = clinician
	       AND holiday.start < appt 
	       AND holiday.finish > appt; 
	IF FOUND THEN
	   RETURN NULL;
	END IF; 
	-- find if slot actually exist.
	SELECT * INTO dummy FROM list, session WHERE
	       session.clinician = clinician AND
	       float8 (session.day) = extract (dow from appt_date) AND
	       -- extract returns float8 for the day of week (????)
	       -- needs to match on other side of =
	       session.id = list.session AND
	       list.time = appt_time;
	IF FOUND THEN
	   RETURN ''f'';
	ELSE
	   RETURN NULL;
	END IF;
END;' LANGUAGE 'plpgsql';

-- To get a list of bookings for a given date, do something like
-- SELECT time, book (1, '10/1/01', time)
-- FROM list WHERE float8 (day) = extract (dow from date '10/1/01') ORDER BY time;

COMMENT ON FUNCTION is_booked (integer, date, time) IS 
'Returns true if a patient is booked, false if not, NULL if time not available';

 

CREATE FUNCTION get_book_patient (INTEGER, DATE, TIME)
RETURNS INTEGER AS '
DECLARE
	doctor ALIAS FOR $1;
	appt_date ALIAS FOR $2;
	appt_time ALIAS FOR $3;
	appt datetime;
	patient_id integer; 
BEGIN
	appt:= timestamp (appt_date, appt_time); 
	SELECT appointment.patient_id INTO patient_id FROM appointment, session
	WHERE appointment.time = appt AND
	      appointment.session = session.id AND
	      session.clinician = doctor;
	RETURN patient_id;
END;' LANGUAGE 'plpgsql';

COMMENT ON FUNCTION get_book_patient (integer, date, time) IS
'Convience function to find the ID of a patient booked at a particular time.';

CREATE FUNCTION isnotonholiday (INTEGER, DATE, TIME)
RETURNS BOOLEAN AS '
DECLARE
	clinician ALIAS FOR $1;
	appt_date ALIAS FOR $2;
	appt_time ALIAS FOR $3;
	appt datetime;
	dummy RECORD;
BEGIN
	appt :=timestamp (appt_date, appt_time); 
	SELECT * INTO dummy FROM holiday WHERE
	       holiday.clinician = clinician
	       AND holiday.start <= appt -- date within holiday range.
	       AND holiday.finish > appt; 
	RETURN NOT FOUND;
END;' LANGUAGE 'plpgsql';

COMMENT ON FUNCTION isnotonholiday (integer, date, time) IS
'Returns true if doctor is NOT on holiday at the specified time.';


-- a function to get the first available appointment for any clinician
CREATE FUNCTION get_first_avail (INTEGER, DATE)
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
