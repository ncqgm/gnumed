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
public interface ClinMedicationFields {
	static String pk_item = "pk_item", brandName = "brandname",  atc_code="atc_code",
	db_origin="db_origin", db_drug_id="db_drug_id",
	amount_unit="amount_unit", dose="dose", 
	period="period", form="form", directions="directions",
	prn="prn", sr="sr",
	started="started",
	last_prescribed="last_prescribed",
	discontinued="discontinued";
}
