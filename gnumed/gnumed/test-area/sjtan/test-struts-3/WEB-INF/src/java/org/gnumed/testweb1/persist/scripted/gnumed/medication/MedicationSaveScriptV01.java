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
import java.util.Calendar;

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
		setLastPrescribedLater(med);
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
		rootItemInserter.setClinRootItemStatement(stmt, med, 14); 
		int i = 0;
		stmt.setString(++i, med.getBrandName());
		stmt.setString(++i, med.getATC_code());
		stmt.setString(++i, med.getDB_origin());
		stmt.setString(++i, med.getDB_drug_id());
		stmt.setString(++i, med.getConvertedAmountUnit());
		//stmt.setDouble(7, med.getConvertedDose());
		
		stmt.setString(++i , "'{ " + String.valueOf(med.getConvertedDose()) + " }'");
		//changed
		stmt.setInt(++i,  med.getPeriod());
		stmt.setString(++i, med.getForm());
		stmt.setString(++i, med.getDirections());
		stmt.setBoolean( ++i, med.isPRN());
		stmt.setTimestamp(++i, new java.sql.Timestamp(med.getStart().getTime()));
		stmt.setTimestamp(++i, new java.sql.Timestamp(med.getLast().getTime()));
		stmt.setTimestamp(++i,med.getDiscontinued() == null? null: new java.sql.Timestamp( med.getDiscontinued().getTime()));
		stmt.setString(++i, "p");
		stmt.setBoolean(++i,  med.isSR());
	}

	/**
	 * @param rootItemInserter
	 * @return
	 */
	public String getInsertStatement(ClinRootInsert rootItemInserter) {
		String s9 = "insert into clin_medication("+
				//pk_item + ", " + 
				brandName + ", " 
				+ atc_code + ", "
				+ db_origin + ", "
				+ db_drug_id + ", " 
				+ amount_unit + ", "  
				+ dose + ", " 
				+ period + ", " 
				+ form + ", " 
				+	directions + ", "
				+ prn + ", " +
				started + ", " 
				+ last_prescribed + ", " +
				discontinued + ", " +
			 	rootItemInserter.getClinRootFields()+ ", " 
			 	+sr  + " ) " 
				+ "values (" +
					//	"?," +
						"  ? , ? , ?,   ?," +
					" ? , ? , ? , ? , ?" +
					", ? , ? , ? , ? , ?" +
					" , ? , ? , ? , ? , ?)";
		return s9;
	}

 

	/**
	 * @param med
	 */
	private void setLastPrescribedLater(EntryMedication med) {
		// TODO Auto-generated method stub
		Calendar cal = Calendar.getInstance();
		cal.setTime(med.getLast());
		//cal.roll(Calendar.MINUTE, true); // TODO: restore 
		cal.roll(Calendar.DATE, true);  // whilst the schema constraint stops it working
		med.setLast(cal.getTime());
	}
 
 
}
