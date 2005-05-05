/*
 * Created on 05-Mar-2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package oscar.oscarDB;

import java.sql.ResultSet;

/**
 * @author sjtan
 *
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
public interface DBHandler {

    /**
     * @param sql
     */
    void RunSQL(String sql);

    /**
     * @param lastInsertedIdSql
     * @return
     */
    ResultSet GetSQL(String lastInsertedIdSql);

}
