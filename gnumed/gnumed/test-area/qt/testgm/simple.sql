create table urb (
	id_urb integer primary key,
	name varchar(200),
	postcode varchar (50),
	state varchar(50)
);
	
create sequence id_patient_sequence start 1;

create table patient ( 
	id_patient integer primary key default nextval('id_patient_sequence'),
	title  varchar(50),
	firstnames varchar(200),
	lastnames varchar(200),
	birthdate date,
	sex char(1),
	address varchar(300),
	phone_home varchar(20),
	phone_work varchar(20),
	public_health_id varchar ( 50),
	public_health_expiry_date date,
	private_health_insurance varchar(50),
	private_health_insurance_no varchar(60),
	private_health_insurance_expiry_date date,
	veterans_affairs_id varchar (50),
	notes text
);

create table lnk_patient_urb( 
	id_patient integer references patient,
	id_urb integer references urb
);

create sequence id_history_sequence start 1;

create table history (
	id_history integer primary key default nextval('id_history_sequence'),
	id_patient integer references patient,
	date_commenced date,
	description varchar(256),
	notes text	
);
create sequence id_allergy_sequence start 1;
create table allergy(
	id_allergy integer primary key default nextval('id_allergy_sequence'),
	id_patient integer references patient,
	date_entered date,
	drugname varchar(100),
	reaction varchar(100),
	notes text
);

create sequence id_prescription_sequence start 1;

create table prescription (
	id_prescription integer primary key default nextval('id_prescription_sequence'),
	id_patient integer references patient,
	date_commenced date,
	date_prescribed date,
	drugname varchar(100),
	qty 	varchar (100),
	dosing 	varchar (255),
	repeats 	integer default 0,
	notes text,
	date_ceased date default null,
	print boolean
);

create sequence id_progress_note_sequence start 1;
create table progress_note (
	id_progress_note integer primary key default nextval('id_progress_note_sequence'),
	id_patient integer references patient,
	date_entered date,
	notes text,
	username varchar(100) default user
);

create sequence id_vaccination_sequence start 1;
create table vaccination (
	id_vaccination integer primary key default nextval('id_vaccination_sequence') ,
	id_patient integer references patient,
	vaccine varchar(100),
	date_given date,
	serial_no varchar(50),
	notes text
);

create sequence id_vaccine_sequence start 1;
create table vaccine (
	name_vaccine varchar(100) primary key default nextval('id_vaccine_sequence'),
	is_generic boolean,
	is_combined boolean,
	indications text,
	usage text
);


create sequence id_investigation_sequence start 1;
create table investigation (
	id_investigation integer primary key default nextval('id_investigation_sequence'),
	id_patient integer references patient,
	test_ordered varchar (512),
	clinical_notes text,
	datetime_ordered timestamp,
	datetime_completed timestamp
);


create sequence id_investigation_result_sequence start 1;
create table investigation_result (
	id_investigation_result integer primary key default nextval('id_investigation_result_sequence'),
	id_investigation integer references investigation,
	id_patient integer references patient,
	result text,
	report_comment text,
	notes text,
	datetime_reported timestamp,
	datetime_received timestamp,
	datetime_checked timestamp,
	checkedby varchar(50)
);

create table specialty (
	name varchar(100) primary key 
) ;


create sequence id_doctor_sequence start 1;
create table doctor (
	id_doctor integer primary key default nextval('id_doctor_sequence'),
	prescriber_no integer,
	firstnames varchar (200),
	lastnames varchar(200),
	title varchar( 50),
	preferred_salutation varchar(200),
	interest_in varchar(500),
	mobile varchar (100),
	pager varchar (100),
	specialty varchar(100) references specialty		
);

create table provider_numbers (
	id_doctor integer references doctor,
	provider_number varchar(100) primary key
);


create sequence id_practice_location_sequence start 1;
create table practice_location(
	id_practice_location integer primary key default nextval('id_practice_location_sequence'),
	practice_name varchar(200),
	address varchar (200),
	id_urb integer references urb,
	work_phone varchar(100),
	work_phone2 varchar(100),
	fax varchar( 100),
	email varchar(100)
);


create table practices_at (
	id_consultant integer primary key,
	date_known_active date,
	date_known_ceased date,
	id_practice_location integer references practice_location
);


create table referral (
	id_doctor integer references doctor,
	id_practice_location integer references practice_location,
	datetime_written timestamp,
	header text,
	body text,
	id_referring_doctor integer references doctor
);



create table billing_item (
	billing_code varchar(40) primary key,
	date_sourced date,
	title varchar (400),
	notes text
);	

create table billing_category (
	billing_category varchar(100) primary key
);




	
	






	
