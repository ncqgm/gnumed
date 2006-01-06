 create table au.med_protocol_element ( narrative text, generic text, adjuvant text, dosage_form text , ufk_drug text not null, drug_db text not null, atc_code text not null, is_cr boolean default false, dosage numeric[] not null , period interval not null, dosage_unit text null, is_paed boolean default false, paed_dose numeric default null, paed_factor text default 'mg/kg' , directions text, is_prn boolean default false) inherits (audit.audit_fields ) ;
 create table au.med_protocol ( pk serial primary key, name text ) inherits (audit.audit_fields);
 alter table au.med_protocol_element add fk_med_protocol integer references au.med_protocol;
 

