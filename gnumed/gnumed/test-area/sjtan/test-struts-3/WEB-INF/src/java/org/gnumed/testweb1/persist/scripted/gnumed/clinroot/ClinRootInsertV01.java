/*
 * Created on 20-Oct-2004
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.persist.scripted.gnumed.clinroot;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.Timestamp;

import org.gnumed.testweb1.data.ClinRootItem;
import org.gnumed.testweb1.data.Vaccination;
import org.gnumed.testweb1.persist.DataSourceException;
import org.gnumed.testweb1.persist.scripted.gnumed.ClinRootInsert;

/**
 * @author sjtan
 * 
 * this sets the common insert fields for a preparedStatement which inserts
 * into a table inheriting from clinRootItem. 
 * The common fields are in clin_root_fields.
 */
public class ClinRootInsertV01 implements ClinRootInsert {
	static String clin_root_fields = " clin_when, narrative, soap_cat,  fk_encounter, fk_episode";
	
	public String getClinRootFields() {
		return clin_root_fields;
	}
	
	/*
	 * (non-Javadoc)
	 * 
	 * @see org.gnumed.testweb1.persist.scripted.gnumed1.ClinRootInsert#setClinRootItemStatement(java.sql.PreparedStatement,
	 *           org.gnumed.testweb1.data.ClinRootItem, int)
	 */

	public void setClinRootItemStatement(PreparedStatement stmt,
			ClinRootItem item, int startIndex) throws DataSourceException,
			SQLException {

		setClinRootItemStatement(stmt, item, startIndex, startIndex + 5);
	}

	/**
	 * gets the next sequence value 
	 * @param connection
	 * @param seqName , the name of the sequence
	 * @return an Integer, the next sequence value
	 * @throws SQLException
	 * @throws DataSourceException
	 */
	public Integer getNextId(Connection conn, String seqName) throws SQLException, DataSourceException {
		Statement stmt = conn.createStatement();
		stmt.execute("select nextval ('" + seqName + "')");
		ResultSet rs = stmt.getResultSet();
		Integer id = null;
		while (rs.next()) {
			id = new Integer(rs.getInt(1));
		}
		if (id == null)
			throw new DataSourceException("id from " + seqName + " was null");
		return id;
	}

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.persist.scripted.gnumed.ClinRootInsert#setClinRootItemStatement(java.sql.PreparedStatement, org.gnumed.testweb1.data.Vaccination, int, int)
     */
    public void setClinRootItemStatement(PreparedStatement stmt, ClinRootItem item, int startIndex, int end) 
    throws DataSourceException,
	SQLException  {
        // TODO Auto-generated method stub

		Integer id = getNextId(stmt.getConnection(),
				"clin_root_item_pk_item_seq");

		stmt.setInt(1, id.intValue());
		for (int i = startIndex; i < end &&  i-startIndex < 5 ;++i) {
		    int n = i - startIndex;
		    switch (n) {
		    
		    case 0:
		    	    stmt.setTimestamp(startIndex++, new Timestamp(item.getClin_when()
					.getTime()));
		    	    break;
		    	
		    case 1:
		    	    stmt.setString(startIndex++, (item.getNarrative() == null ? "" : item
					.getNarrative()));
		    	    break;
			
			case 2:
				    stmt.setString(startIndex++, item.getSoapCat().substring(0, 1));
				    break;
			
			case 3:
			    stmt.setInt(startIndex++, item.getEncounter().getId().intValue());
			    break;
			
			case 4:
			    stmt.setInt(startIndex++, item.getEpisode().getId().intValue());
			    break;
		    
			default: 
			    break;
		    }
		    
		}
		
    }
}