/*
 * Created on 20-Oct-2004
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.persist.scripted.gnumed;

import java.sql.Connection;
import java.sql.SQLException;

import org.gnumed.testweb1.data.EntryMedication;
import org.gnumed.testweb1.data.HealthSummary01;
import org.gnumed.testweb1.persist.DataSourceException;

/**
 * @author sjtan
 *
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
public interface MedicationSaveScript {
	void save(Connection conn, EntryMedication med, HealthSummary01 summary, ClinRootInsert inserter) throws SQLException , DataSourceException ;

}
