/*
 * Created on 20-Oct-2004
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.persist.scripted.gnumed.medication;

import java.sql.PreparedStatement;
import java.sql.SQLData;
import java.sql.SQLException;
import java.sql.Types;
import java.util.Date;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.gnumed.testweb1.data.EntryMedication;
import org.gnumed.testweb1.persist.DataSourceException;
import org.gnumed.testweb1.persist.scripted.gnumed.ClinRootInsert;
import org.gnumed.testweb1.persist.scripted.gnumed.MedicationSaveScript;

/**
 * @author sjtan
 * 
 * TODO To change the template for this generated type comment go to Window -
 * Preferences - Java - Code Style - Code Templates
 */
public class MedicationSaveScriptV02 extends MedicationSaveScriptV01 implements
		MedicationSaveScript, ClinMedicationFieldsV02 {
	static Log log = LogFactory.getLog(MedicationSaveScriptV02.class);

	static String generic_name = "generic";

	static String INTERVAL_YEAR = "year", INTERVAL_MONTHS = "mons",
			INTERVAL_DAYS = "days", INTERVAL_HOURS = "h";

	/**
	 * @param med
	 * @param rootItemInserter
	 * @param stmt
	 * @throws DataSourceException
	 * @throws SQLException
	 */
 
	
	
	protected void setStatement(EntryMedication med,
			ClinRootInsert rootItemInserter, PreparedStatement stmt)
			throws DataSourceException, SQLException {
 
		int j = 0;
		stmt.setString(++j, med.getBrandName());  //+1
		stmt.setString(++j, med.getATC_code());	//+2
		stmt.setString(++j, med.getDB_origin()); //+3
		stmt.setString(++j, med.getDB_drug_id());//+4
		stmt.setString(++j, med.getConvertedAmountUnit()); //+5
		//stmt.setDouble(++j, med.getConvertedDose());

		stmt
				.setString(++j, "{" + String.valueOf(med.getConvertedDose())
						+ " }"); //+6
		//changed
		stmt.setString(++j, String.valueOf(med.getPeriod()) + INTERVAL_HOURS);//+7
		stmt.setString(++j, med.getForm());//+8
		stmt.setString(++j, med.getDirections());  //+9
 
		stmt.setBoolean(++j, med.isPRN()); //+10
		stmt.setBoolean(++j, med.isSR());//+11
		//	stmt.setDate(++j, new java.sql.Date(med.getStart().getTime()));
		// //deprecated
		stmt.setTimestamp(++j, new java.sql.Timestamp(med.getLast().getTime())); //+12
		
		stmt.setTimestamp(++j, med.getDiscontinued() == null ? null
				: new java.sql.Timestamp(med.getDiscontinued().getTime())); //+13
		stmt.setString( ++j, med.getGenericName() == null ? "" : med.getGenericName() ); // +14
		//+14
		med.setSoapCat("p"); 
		
		rootItemInserter.setClinRootItemStatement(stmt, med, ++j);
	
		
	}

	/**
	 * @param rootItemInserter
	 * @return
	 */
	public String getInsertStatement(ClinRootInsert rootItemInserter) {
		String s9 = "insert into clin_medication("
				//+ ClinMedicationFieldsV02.pk_item + ", "
				+ ClinMedicationFieldsV02.brandName + ", "
				+ ClinMedicationFieldsV02.atc_code + ", "
				+ ClinMedicationFieldsV02.db_origin + ", "
				+ ClinMedicationFieldsV02.db_drug_id + ", "
				+ ClinMedicationFieldsV02.amount_unit + ", "
				+ ClinMedicationFieldsV02.dose + ", "
				+ ClinMedicationFieldsV02.period + ", "
				+ ClinMedicationFieldsV02.form + ", "
				+ ClinMedicationFieldsV02.directions + ", "
				+ ClinMedicationFieldsV02.prn + ", " +
				 ClinMedicationFieldsV02.sr + ", " 
				// + started +", " //-
				
												// deprecated to clin_when?
				+ ClinMedicationFieldsV02.last_prescribed + ", "
				+ ClinMedicationFieldsV02.discontinued + ", "   // 13
				+ generic_name +	", " +// 14 
				// fields
				// here
				rootItemInserter.getClinRootFields()  // +5
				
				+ "  ) "

				+ "values (" +
				// "?,  " +
				"? , ? , ?, ?,  " + //4
				"?, ? , ? , ? , ? , " +
				"?, ? , ? , ? , ? , " +
				"?, ? , ? , ? , ?)"; 
				//19 fields
		return s9;
	}

}