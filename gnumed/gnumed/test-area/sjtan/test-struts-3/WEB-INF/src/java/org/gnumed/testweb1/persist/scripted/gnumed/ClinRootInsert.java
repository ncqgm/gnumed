/*
 * Created on 20-Oct-2004
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.persist.scripted.gnumed;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;

import org.gnumed.testweb1.data.ClinRootItem;
import org.gnumed.testweb1.data.Vaccination;
import org.gnumed.testweb1.persist.DataSourceException;

/**
 * @author sjtan
 *
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
public interface ClinRootInsert {
	public String getClinRootFields() ;
	 void setClinRootItemStatement(PreparedStatement stmt,
			ClinRootItem item, int startIndex) throws DataSourceException,
			SQLException ;
	 
	 Integer getNextId(Connection connection, String string) throws SQLException, DataSourceException ;
    /**
     * @param stmt
     * @param vacc
     * @param i
     * @param j
     * @throws SQLException
     * @throws DataSourceException
     */
    public void setClinRootItemStatement(PreparedStatement stmt, ClinRootItem item, int i, int j) throws DataSourceException, SQLException;
		
}
