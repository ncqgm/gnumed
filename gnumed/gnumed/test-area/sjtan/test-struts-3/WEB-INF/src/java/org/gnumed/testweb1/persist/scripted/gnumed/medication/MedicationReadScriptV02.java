/*
 * Created on 21-Oct-2004
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.persist.scripted.gnumed.medication;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Date;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.gnumed.testweb1.data.Medication;
import org.gnumed.testweb1.data.MedicationImpl1;
import org.gnumed.testweb1.persist.scripted.gnumed.MedicationReadScript;

/**
 * @author sjtan
 * 
 * TODO To change the template for this generated type comment go to Window -
 * Preferences - Java - Code Style - Code Templates
 */
public class MedicationReadScriptV02 implements ClinMedicationFieldsV02,
 
 MedicationReadScript {
	Log log = LogFactory.getLog(MedicationReadScriptV02.class);
	/*
	 * (non-Javadoc)
	 * 
	 * @see org.gnumed.testweb1.persist.scripted.gnumed.MedicationReadScript#read(java.sql.ResultSet)
	 */
	public Medication read(ResultSet set) throws SQLException {
		Medication m = new MedicationImpl1();
		m.setATC_code(set.getString(ClinMedicationFieldsV02.atc_code));
		m.setBrandName(set.getString(ClinMedicationFieldsV02.brandName));
		m.setGenericName(set.getString(ClinMedicationFieldsV02.generic));
		m.setDB_origin(set.getString(ClinMedicationFieldsV02.db_origin));
		m.setDB_drug_id(set.getString(ClinMedicationFieldsV02.db_drug_id));
//		ResultSet doses = set.getArray(ClinMedicationFieldsV02.dose)
//				.getResultSet();
//		if (doses.next()) {
//			m.setConvertedDose(doses.getDouble(1));
//		}
		String doseStr = set.getString(ClinMedicationFieldsV02.dose);
		if (doseStr.indexOf('{') == 0  && dose.endsWith("}") ) {
			doseStr = doseStr.substring(1, doseStr.length() -2);
			String[] doseStrings  = doseStr.split("\\s*, \\s*");
			if (doseStrings.length > 0) {
				try {
				m.setConvertedDose(Double.parseDouble(doseStrings[0]));
				} catch (Exception e) {
					log.info("FAILED TO PARSE doseStr= " + doseStr ,e);
				}
			} else {
				log.info("FAILED TO PARSE doseStr=" + doseStr );
			}
		}
		m.setDirections(set.getString(ClinMedicationFieldsV02.directions));
		m.setLast(new Date(set.getTimestamp(
				ClinMedicationFieldsV02.last_prescribed).getTime()));
		m.setStart(new Date(set.getTimestamp("clin_when").getTime()));
		if (set.getTimestamp(ClinMedicationFieldsV02.discontinued) != null) {
			m.setDiscontinued(new Date(set.getTimestamp(
					ClinMedicationFieldsV02.discontinued).getTime()));
		} 
		return m;

	}

}