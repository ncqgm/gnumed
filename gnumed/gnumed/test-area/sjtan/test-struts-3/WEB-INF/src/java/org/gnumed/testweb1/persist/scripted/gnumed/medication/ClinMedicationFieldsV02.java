/*
 * Created on 21-Oct-2004
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.persist.scripted.gnumed.medication;

/**
 * @author sjtan
 *
 * medication table fields as string variables for compiler checking.
 * gnumed-> \d clin_medication
                                          Table "public.clin_medication"
     Column      |           Type           |                              Modifiers
-----------------+--------------------------+---------------------------------------------------------------------
 pk_audit        | integer                  | not null default nextval('public.audit_fields_pk_audit_seq'::text)
 row_version     | integer                  | not null default 0
 modified_when   | timestamp with time zone | not null default ('now'::text)::timestamp(6) with time zone
 modified_by     | name                     | not null default "current_user"()
 pk_item         | integer                  | not null default nextval('public.clin_root_item_pk_item_seq'::text)
 clin_when       | timestamp with time zone | not null default ('now'::text)::timestamp(6) with time zone
 fk_encounter    | integer                  | not null
 fk_episode      | integer                  | not null
 narrative       | text                     |
 soap_cat        | text                     |
 pk              | integer                  | not null default nextval('public.clin_medication_pk_seq'::text)
 last_prescribed | date                     | not null default ('now'::text)::date
 fk_last_script  | integer                  |
 discontinued    | date                     |
 brandname       | text                     |
 generic         | text                     |
 adjuvant        | text                     |
 dosage_form     | text                     | not null
 ufk_drug        | text                     | not null
 drug_db         | text                     | not null
 atc_code        | text                     | not null
 is_cr           | boolean                  | not null
 dosage          | numeric[]                | not null
 period          | interval                 | not null
 dosage_unit     | text                     | not null
 directions      | text                     |
 is_prn          | boolean                  | default false
Indexes:
    "clin_medication_pkey" primary key, btree (pk)
    "idx_clin_medication" btree (discontinued) WHERE (discontinued IS NOT NULL)
    "idx_cmeds_encounter" btree (fk_encounter)
    "idx_cmeds_episode" btree (fk_episode)
Check constraints:
    "clin_root_item_soap_cat" CHECK (soap_cat = 's'::text OR soap_cat = 'o'::text OR soap_cat = 'a'::text OR soap_cat = 'p'::text)
    "clin_medication_dosage_unit" CHECK (dosage_unit = 'g'::text OR dosage_unit = 'each'::text OR dosage_unit = 'ml'::text)
    "medication_is_plan" CHECK (soap_cat = 'p'::text)
    "brand_or_generic_required" CHECK (brandname IS NOT NULL OR generic IS NOT NULL)
    "prescribed_after_started" CHECK (last_prescribed >= clin_when::date)

 */
public interface ClinMedicationFieldsV02 extends ClinMedicationFields {
	static String
		db_origin = "drug_db",
		db_drug_id = "ufk_drug",
		amount_unit = "dosage_unit",
		form = "dosage_form",
		dose = "dosage", // now an array of float or double
		period = "period", // now a string year, mons, days
									 // hh:mm:ss.msec
		prn = "is_prn", sr="is_cr",
	//	 started="clin_when";
		generic="generic",
		discontinued = "discontinued",
		directions = "directions";
}
