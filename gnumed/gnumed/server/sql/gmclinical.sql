-- $REVISION=1.0$

create table enum_clinical_encounters(
	id SERIAL primary key,
	description text
)inherits {audit_clinical);


INSERT INTO enum_clinical_encounters (description)
	values ('surgery consultation');
INSERT INTO enum_clinical_encounters (description)
	values ('phone consultation');
INSERT INTO enum_clinical_encounters (description)
	values ('fax consultation');
INSERT INTO enum_clinical_encounters (description)
	values ('home visit');
INSERT INTO enum_clinical_encounters (description)
	values ('nursing home visit');
INSERT INTO enum_clinical_encounters (description)
	values ('repeat script');
INSERT INTO enum_clinical_encounters (description)
	values ('hospital visit');
INSERT INTO enum_clinical_encounters (description)
	values ('video conference');
INSERT INTO enum_clinical_encounters (description)
	values ('proxy encounter');
INSERT INTO enum_clinical_encounters (description)
	values ('emergency encounter');
INSERT INTO enum_clinical_encounters (description)
	values ('other encounter');

COMMENT ON TABLE enum_clinical_encounters is
'these are the types of encounter';


create table clinical_transaction(
	id SERIAL primary key,
	gmt_time timestamp,
	timezone_ID int,
	location_ID int,
	doctor_ID int,
	patient_ID int,
	enum_clinical_encounters_ID int REFERENCES (enum_clinical_encounters)
) inherits {audit_clinical);

COMMENT ON TABLE clinical_transaction is
'unique identifier for clinical encounter';

create table enum_clinical_history(
	id SERIAL primary key,
	description text
) inherits {audit_clinical);

COMMENT ON TABLE enum_clinical_history is
'types of history taken during a clinical encounter';


INSERT INTO enum_clinical_history (description)
	values ('past');
INSERT INTO enum_clinical_history (description)
	values ('presenting complaint');
INSERT INTO enum_clinical_history (description)
	values ('history of present illness');
INSERT INTO enum_clinical_history (description)
	values ('social');
INSERT INTO enum_clinical_history (description)
	values ('family');
INSERT INTO enum_clinical_history (description)
	values ('immunisation');
INSERT INTO enum_clinical_history (description)
	values ('requests');
INSERT INTO enum_clinical_history (description)
	values ('allergy');
INSERT INTO enum_clinical_history (description)
	values ('drug');
INSERT INTO enum_clinical_history (description)
	values ('sexual');
INSERT INTO enum_clinical_history (description)
	values ('psychiatric');
INSERT INTO enum_clinical_history (description)
	values ('other');

create table clinical_history(
	id SERIAL primary key,
	enum_clinical_history_ID int REFERENCES(enum_clinical_history),
	clinical_transaction_ID int  REFERENCES(clinical_transaction),
	timestamp timestamp DEFAULT now(),
	text text
)inherits {audit_clinical);

COMMENT ON TABLE clinical_history is
'narrative details of history taken during a clinical encounter';

create table enum_coding_systems (
	id SERIAL primary key,
	description text
)inherits {audit_clinical);


INSERT INTO enum_coding_systems (description)
	values ('general');
INSERT INTO enum_coding_systems (description)
	values ('clinical');
INSERT INTO enum_coding_systems (description)
	values ('diagnosis');
INSERT INTO enum_coding_systems (description)
	values ('therapy');
INSERT INTO enum_coding_systems (description)
	values ('pathology');
INSERT INTO enum_coding_systems (description)
	values ('bureaucratic');
INSERT INTO enum_coding_systems (description)
	values ('ean');
INSERT INTO enum_coding_systems (description)
	values ('other');


create table coding_systems (
	id SERIAL primary key,
	enum_coding_systems_ID int REFERENCES(enum_coding_systems),
	description text,
	version char(6),
	deprecated timestamp
)inherits {audit_clinical);


create table clinical_diagnosis (
	id SERIAL primary key,
	clinical_transaction_ID int  REFERENCES(clinical_transaction),
	timestamp timestamp DEFAULT now(),
	approximate_start text DEFAULT null,
	code char(16),
	coding_systems_ID int REFERENCES (coding_systems),
	text text
)inherits {audit_clinical);


create table enum_confidentiality_level (
	id SERIAL primary key,
	description text
)inherits {audit_clinical);


INSERT INTO enum_confidentiality_level (description)
	values ('public');
INSERT INTO enum_confidentiality_level (description)
	values ('relatives');
INSERT INTO enum_confidentiality_level (description)
	values ('receptionist');
INSERT INTO enum_confidentiality_level (description)
	values ('clinical staff');
INSERT INTO enum_confidentiality_level (description)
	values ('doctors');
INSERT INTO enum_confidentiality_level (description)
	values ('doctors of practice only');
INSERT INTO enum_confidentiality_level (description)
	values ('treating doctor');

create table clinical_diagnosis_extra (
	id SERIAL primary key,
	clinical_diagnosis_ID int REFERENCES (clinical_diagnosis),
	confidential int,

)inherits {audit_clinical);
COMMENT ON TABLE clinical_diagnosis is
'';
