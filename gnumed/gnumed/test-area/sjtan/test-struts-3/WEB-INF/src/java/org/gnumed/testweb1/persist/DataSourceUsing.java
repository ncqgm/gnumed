/*
 * DataSourceUsing.java
 *
 * Created on June 21, 2004, 1:34 AM
 */

package org.gnumed.testweb1.persist;
import javax.sql.DataSource;
/**
 *
 * @author  sjtan
 */
public interface DataSourceUsing {
    public void setDataSource(DataSource ds);
    public DataSource getDataSource();
}
