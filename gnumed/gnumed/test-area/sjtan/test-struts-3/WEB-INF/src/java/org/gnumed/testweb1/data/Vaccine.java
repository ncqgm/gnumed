/*
 * Vaccine.java
 *
 * Created on July 5, 2004, 8:41 PM
 */

package org.gnumed.testweb1.data;

/**
 *
 * @author  sjtan
 */
public interface Vaccine {
    public String getDescriptiveName();
    public Integer getId();
    public void setId(Integer id);
    public String getShortName();
    public String getTradeName();
    public String getDescription();
    public boolean isLive();
    public void setLastBatchNo(String batchNo);
    public String getLastBatchNo();
}
