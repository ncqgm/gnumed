/*
 * NullRootItem.java
 *
 * Created on September 26, 2004, 4:28 PM
 */

package org.gnumed.testweb1.data;
import java.util.Date;
/**
 *
 * @author  sjtan
 */
public class NullRootItem
 implements ClinRootItem {
    public static NullRootItem NullItem ;
    static {
        NullItem = new NullRootItem();
    }
    /** Creates a new instance of NullRootItem */
    NullRootItem() {
    }
    
    public java.util.Date getClin_when() {
        return new Date();
    }
    
    public ClinicalEncounter getEncounter() {
        return null;
    }
    
    public ClinicalEpisode getEpisode() {
        return null;
    }
    
    public String getHealthIssueName() {
        return "";
    }
    
    public Long getId() {
        return null;
    }
    
    public String getNarrative() {
        return null;
    }
    
    public String getNewHealthIssueName() {
        return "";
    }
    
    public Integer getPk() {
        return null;
    }
    
    public String getSoapCat() {
         return null;
    }
    
    public boolean isLinkedToPreviousEpisode() {
         return false;
    }
    
    public void setClin_when(java.util.Date clin_when) {
    }
    
    public void setEncounter(ClinicalEncounter encounter) {
    }
    
    public void setEpisode(ClinicalEpisode episode) {
    }
    
    public void setHealthIssueName(String healthIssueName) {
    }
    
    public void setId(Long id) {
    }
    
    public void setLinkedToPreviousEpisode(boolean isLinkedToPreviousEpisode) {
    }
    
    public void setNarrative(String narrative) {
    }
    
    public void setNewHealthIssueName(String newHealthIssueName) {
    }
    
    public void setPk(Integer pk) {
    }
    
    public void setSoapCat(String soapCat) {
    }

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.ClinRootItem#normalizeHealthIssueName()
	 */
	public void normalizeHealthIssueName() {
		// TODO Auto-generated method stub
		
	}
    
}
