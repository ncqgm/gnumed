/*
 * Created on 21-Oct-2004
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.persist.scripted.gnumed;

import java.sql.ResultSet;
import java.sql.SQLException;

import org.gnumed.testweb1.data.Medication;

/**
 * @author sjtan
 *
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
public interface MedicationReadScript {
	public Medication read( ResultSet set) throws SQLException;
}
