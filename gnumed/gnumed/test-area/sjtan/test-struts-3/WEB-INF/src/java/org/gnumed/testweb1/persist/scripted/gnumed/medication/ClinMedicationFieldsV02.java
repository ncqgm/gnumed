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
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Style - Code Templates
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
		prn = "is_prn",
	//	 started="clin_when";
		generic="generic";
}
