/*
 * Created on 20-Oct-2004
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.persist.scripted.gnumed.medication;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;

import org.gnumed.testweb1.data.EntryMedication;
import org.gnumed.testweb1.data.HealthSummary01;
import org.gnumed.testweb1.persist.DataSourceException;
import org.gnumed.testweb1.persist.scripted.gnumed.ClinRootInsert;
import org.gnumed.testweb1.persist.scripted.gnumed.MedicationSaveScript;

/**
 * @author sjtan
 *
 * 
 * Window - Preferences - Java - Code Style - Code Templates
 */
public class MedicationSaveScriptV01 implements MedicationSaveScript, ClinMedicationFields {
	
 
	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.persist.scripted.gnumed1.MedicationSaveScript#save(java.sql.Connection, org.gnumed.testweb1.data.EntryMedication, org.gnumed.testweb1.data.HealthSummary01)
	 */
	public void save(Connection conn, EntryMedication med,
			HealthSummary01 summary, ClinRootInsert  rootItemInserter) throws SQLException, DataSourceException {
		
		String s9 = getInsertStatement(rootItemInserter);
		PreparedStatement stmt = conn.prepareStatement(s9);
		
		setStatement(med, rootItemInserter, stmt);
             
		stmt.execute();
        conn.commit();
	}

	/**
	 * @param med
	 * @param rootItemInserter
	 * @param stmt
	 * @throws DataSourceException
	 * @throws SQLException
	 */
	protected void setStatement(EntryMedication med, ClinRootInsert rootItemInserter, PreparedStatement stmt) throws DataSourceException, SQLException {
		rootItemInserter.setClinRootItemStatement(stmt, med, 15); 
		stmt.setString(2, med.getBrandName());
		stmt.setString(3, med.getATC_code());
		stmt.setString(4, med.getDB_origin());
		stmt.setString(5, med.getDB_drug_id());
		stmt.setString(6, med.getConvertedAmountUnit());
		//stmt.setDouble(7, med.getConvertedDose());
		
		stmt.setString(7 , "'{ " + String.valueOf(med.getConvertedDose()) + " }'");
		//changed
		stmt.setInt(8,  med.getPeriod());
		stmt.setString(9, med.getForm());
		stmt.setString(10, med.getDirections());
		stmt.setBoolean( 11, med.isPRN());
		stmt.setDate(12, new java.sql.Date(med.getStart().getTime()));
		stmt.setDate(13, new java.sql.Date(med.getLast().getTime()));
		stmt.setDate(14,med.getDiscontinued() == null? null: new java.sql.Date( med.getDiscontinued().getTime()));
		stmt.setString(17, "p");
		stmt.setBoolean(20,  med.isSR());
	}

	/**
	 * @param rootItemInserter
	 * @return
	 */
	public String getInsertStatement(ClinRootInsert rootItemInserter) {
		String s9 = "insert into clin_medication("+
				pk_item + ", " + brandName + ", " 
				+ atc_code + ", " + db_origin
				+ ", " + db_drug_id + ", " + amount_unit + ", " +
				dose + ", " + period + ", " + 
				form + ", " +	directions + ", "
				+ prn + ", " +
				started + ", " + last_prescribed + ", " +
				discontinued + ", " +
			 	rootItemInserter.getClinRootFields()+ ", " +sr  + " ) " 
				+ "values (?,  ? , ? , ?,   ?," +
					" ? , ? , ? , ? , ?" +
					", ? , ? , ? , ? , ?" +
					" , ? , ? , ? , ? , ?)";
		return s9;
	}
 
}
