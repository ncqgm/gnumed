/*
 * ClinRootItemImpl1.java
 *
 * Created on September 17, 2004, 11:29 PM
 */

package org.gnumed.testweb1.data;

/**
 *
 * @author  sjtan
 */
public class ClinRootItemImpl1 implements ClinRootItem {
    java.util.Date clin_when = new java.util.Date();
    ClinicalEpisode episode;
    ClinicalEncounter clinicalEncounter;
    Long id;
    char soapCat = 's';
    String narrative, healthIssueName, newHealthIssueName;
    
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
    
    public char getSoapCat() {
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
    
    public void setSoapCat(char soapCat) {
        this.soapCat = soapCat;
    }
    
    public Integer getPk() {
        return new Integer(id.intValue());
    }
    
    public void setPk(Integer pk) {
        this.id = new Long(pk.longValue());
    }
     
    public String getHealthIssueName() {
        return healthIssueName;
    }    
    
    public void setHealthIssueName(String healthIssueName) {
        this.healthIssueName = healthIssueName;
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
    
}
