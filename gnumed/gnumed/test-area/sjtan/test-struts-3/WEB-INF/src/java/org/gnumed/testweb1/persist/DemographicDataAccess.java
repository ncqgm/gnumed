/*
 * DemographicsDataAccess.java
 *
 * Created on June 21, 2004, 12:59 AM
 */

package org.gnumed.testweb1.persist;
import org.gnumed.testweb1.data.DemographicDetail;
import java.util.Date;
import org.apache.struts.config.ModuleConfig;
/**
 *
 * @author  sjtan
 */
public interface DemographicDataAccess {
    public final static String DEMOGRAPHIC_ACCESS = "DemographicDataAccess";
    public DemographicDetail save(DemographicDetail detail) throws DataSourceException;
    public DemographicDetail findDemographicDetailById(final Long id) throws DataSourceException;
public DemographicDetail[] findDemographicDetail( DemographicDetail fragment) throws DataSourceException;
    

}
