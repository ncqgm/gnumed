/*
 * DataObjectFactory.java
 *
 * Created on June 19, 2004, 5:24 PM
 */

package org.gnumed.testweb1.data;

/**
 *
 * @author  sjtan
 */
public interface DataObjectFactory {
    DemographicDetail createDemographicDetail();
    Vaccine createVaccine( String tradeName, String shortName, boolean isLive, String lastBatchNo ) ;
    
}
