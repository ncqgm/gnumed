/*
 * ClinRootItemImpl1.java
 *
 * Created on September 17, 2004, 11:29 PM
 */

package org.gnumed.testweb1.data;

import java.util.HashMap;
import java.util.Map;

import org.gnumed.testweb1.global.Util;
import org.gnumed.testweb1.global.Constants.Schema;

/**
 * The base class for  clinical items such as narratives, vaccinations, medications, lab requests.
 * @author  sjtan
 */
public class ClinRootItemImpl1 implements ClinRootItem, Comparable {
    static Map soapOrder;
    static {
           soapOrder = new HashMap();
           String soap = Schema.SOAP_CAT_FOR_CLINROOT_SORT;
           for (int i = 0; i < soap.length(); ++i) {
               String cat = soap.substring( i, i+1);
               soapOrder.put(cat, new Integer(i));
           }
    };
    
    java.util.Date healthIssueStart = new java.util.Date();
   
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
  //      System.err.println("Get narrative ()" + this);
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
 //       System.err.println("setNarrative " + this);
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

    /** this method sorts ClinRootItems according to their soap category.
     * 
     * @see java.lang.Comparable#compareTo(java.lang.Object)
     */
    public int compareTo(Object o) {
       // System.err.println("Comparing " + o + " with " + this);
        if (o == null)
            return -1;
        
        if ( !ClinRootItem.class.isAssignableFrom(o.getClass())) {
            return -1;
        }
        
        ClinRootItem other = (ClinRootItem)o;
        
        
        
//      System.err.println("Comparing " + getSoapCat() + " with " + other.getSoapCat());
        Integer otherRank = (Integer)soapOrder.get(other.getSoapCat());
        Integer rank = (Integer)soapOrder.get(getSoapCat());
        
        if (otherRank == null)
            return -1;
        if (rank == null)
            return 1;
//      System.err.println("returning comparison of " + rank + " with " + otherRank);
        int result = rank.intValue() - otherRank.intValue();
        if (result != 0)
            return result;
        
        if (other.getClin_when().after(getClin_when())) {
            return -1;
        }
        if (other.getClin_when().before(getClin_when()) ){
            return 1;
        }
        
        return 0;
    }
    /**
     * @return Returns the healthIssueStart.
     */
    public java.util.Date getHealthIssueStart() {
        return healthIssueStart;
    }
    /**
     * @param healthIssueStart The healthIssueStart to set.
     */
    public void setHealthIssueStart(java.util.Date healthIssueStart) {
        this.healthIssueStart = healthIssueStart;
    }
}
