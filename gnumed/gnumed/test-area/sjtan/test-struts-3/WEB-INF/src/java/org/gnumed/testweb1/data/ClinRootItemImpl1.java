/*
 * ClinRootItemImpl1.java
 *
 * Created on September 17, 2004, 11:29 PM
 */

package org.gnumed.testweb1.data;

import org.gnumed.testweb1.global.Util;
import org.gnumed.testweb1.global.Constants.Schema;

/**
 *
 * @author  sjtan
 */
public class ClinRootItemImpl1 implements ClinRootItem {
     
    java.util.Date clin_when = new java.util.Date();
    ClinicalEpisode episode;
    ClinicalEncounter clinicalEncounter;
    Long id;
    boolean isLinkedToPreviousEpisode = false;
    
    String narrative, healthIssueName, newHealthIssueName;
    String soapCat = "s";
    
    /** Creates a new instance of ClinRootItemImpl1 */
    public ClinRootItemImpl1() {
    }
    
    public ClinicalEncounter getEncounter() {
        return clinicalEncounter;
    }
    
    public ClinicalEpisode getEpisode() {
        return episode;
    }
    
    public Long getId() {
        return id;
    }
    
    public String getNarrative() {
        System.err.println("Get narrative ()" + this);
        return narrative;
    }
    
    public String getSoapCat() {
    return soapCat;
    }
    
    public void setEncounter(ClinicalEncounter encounter) {
       this. clinicalEncounter = encounter;
    }
    
    public void setEpisode(ClinicalEpisode episode) {
        
        this.episode = episode;
        episode.setRootItem(episode.getRootItemCount(), this);
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public void setNarrative(String narrative) {
        this.narrative = narrative;
        System.err.println("setNarrative " + this);
    }
    
    public void setSoapCat(String soapCat) {
        this.soapCat = soapCat;
    }
    
    public Integer getPk() { 
        if (id == null)
            return null;
        return new Integer(id.intValue());
    }
    
    public void setPk(Integer pk) {
        this.id = new Long(pk.longValue());
    }
     
    public String getHealthIssueName() {
        return getEpisode().getHealthIssue().getDescription();
    }    
    
    public void setHealthIssueName(String healthIssueName) {
        getEpisode().getHealthIssue().setDescription(healthIssueName);
    }
    
    public java.util.Date getClin_when() {
        return clin_when;
    }
    
    public void setClin_when(java.util.Date clin_when) {
        this.clin_when = clin_when;
    }
    
    public String getNewHealthIssueName() {
        return newHealthIssueName;
    }
    
    public void setNewHealthIssueName(String newHealthIssueName) {
        this.newHealthIssueName = newHealthIssueName;
    }
    
    
    /** makes healthissue name non-null, default xxxDEFAULTxxxx */
    public void normalizeHealthIssueName( ) {
        
        String healthIssueName =  getHealthIssueName();
        String newName =  Util.nullIsBlank( getNewHealthIssueName());
        
        healthIssueName = Util.nullIsBlank(healthIssueName);
        if ( ! "".equals(newName)  ) {
        	healthIssueName = newName;
        } else   if (healthIssueName.equals("")) {
            healthIssueName = Schema.DEFAULT_HEALTH_ISSUE_LABEL;
        }
        
        setNewHealthIssueName("");
        setHealthIssueName(healthIssueName);
         
    }
}
