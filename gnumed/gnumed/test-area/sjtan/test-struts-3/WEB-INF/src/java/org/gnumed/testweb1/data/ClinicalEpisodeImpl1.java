/*
 * ClinicalEpisodeImpl.java
 *
 * Created on September 19, 2004, 8:30 AM
 */

package org.gnumed.testweb1.data;

/**
 *
 * @author  sjtan
 */
public class ClinicalEpisodeImpl1 implements ClinicalEpisode{
    private String description;
    private HealthIssue hi;
    private Long id;
    private java.util.Date modified_when;
    
    private java.util.List rootItems = new java.util.ArrayList();
    
    
    /** Creates a new instance of ClinicalEpisodeImpl */
    public ClinicalEpisodeImpl1()  {
    }
    
    public String getDescription() {
        return description;
    }
    
    public HealthIssue getHealthIssue() {
        return hi;
    }
    
    public Long getId() {
        return id;
    }
    
    public void setDescription(String description) {
        this.description = description;
    }
    
    public void setHealthIssue(HealthIssue healthIssue) {
        this.hi = healthIssue;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public java.util.Date getModified_when() {
        return modified_when;
    }
    
    public void setModified_when(java.util.Date modified_when) {
        this.modified_when = modified_when;
    }
    
    
    
    public ClinRootItem getRootItem(int index) {
        return (ClinRootItem) rootItems.get(index);
    }    
    
    public void setRootItem(int index, ClinRootItem rootItem) {
        if  ( rootItems.size() > index) {
            rootItems.set(index, rootItem);
        } else {
            rootItems.add(rootItem);
        }
    }
    
    public int getRootItemCount() {
        return rootItems.size();
    }
    
    public java.util.List getRootItems() {
        return rootItems;
    }
    
}
