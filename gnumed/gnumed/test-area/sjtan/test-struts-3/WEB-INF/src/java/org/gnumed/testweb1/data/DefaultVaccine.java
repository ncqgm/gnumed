/*
 * DefaultVaccine.java
 *
 * Created on July 6, 2004, 12:42 AM
 */

package org.gnumed.testweb1.data;
import org.gnumed.testweb1.data.Vaccine;
import java.beans.*;
import java.io.Serializable;

/**
 * @author sjtan
 */
public class DefaultVaccine extends Object implements Serializable, Vaccine {
    
   private PropertyChangeSupport propertySupport;
    
    /**
     * Holds value of property id.
     */
    private Integer id;
    
    private String tradeName;
    
    private String shortName;
    
    private String lastBatchNo;
    
    private boolean isLive;
    /**
     * Holds value of property descriptiveName.
     */
    private String descriptiveName;
    
    private String description;
    public DefaultVaccine() {
        propertySupport = new PropertyChangeSupport(this);
    }
    
    public DefaultVaccine( String tradeName, String shortName, boolean isLive, String lastBatchNo) {
        this.tradeName = tradeName;
        this.shortName = shortName;
        this.isLive = isLive;
        this.lastBatchNo = lastBatchNo;
        
    }
    
    public void addPropertyChangeListener(PropertyChangeListener listener) {
        propertySupport.addPropertyChangeListener(listener);
    }
    
    public void removePropertyChangeListener(PropertyChangeListener listener) {
        propertySupport.removePropertyChangeListener(listener);
    }
    
    /**
     * Getter for property id.
     * @return Value of property id.
     */
    public Integer getId() {
        return this.id;
    }
    
    /**
     * Setter for property id.
     * @param id New value of property id.
     */
    public void setId(Integer id) {
        this.id = id;
    }
    
    /**
     * Getter for property description.
     * @return Value of property description.
     */
    public String getDescriptiveName() {
        return  ""+ shortName + " : " + tradeName ;
    }
    
    
    
    public String getDescription() {
        return description;
    }
    
    public String getShortName() {
        return shortName;
    }
    
    public String getTradeName() {
        return tradeName;
    }
    
    public boolean isLive() {
    return isLive;
    }
    
    public String getLastBatchNo() {
        return lastBatchNo;
    }
    
    public void setLastBatchNo(String lastBatchNo) {
        this.lastBatchNo = lastBatchNo;
    }
    
    final static DefaultVaccine nullVaccine;
    static {
        nullVaccine = new DefaultVaccine("","",false,"");
    }
}
