
/** Java class "script_drug.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package  org.gnumed.gmClinical;

import java.util.*;
import org.drugref.package_size;
import org.gnumed.gmIdentity.identity;

/**
 * <p>
 * 
 * </p>
 * @hibernate.class
 */
public class script_drug {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private String directions; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String adjuvant; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private Double dose_amount; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private int frequency; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private Boolean prn; 

    private Boolean _current;
   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    package_size package_size;
/**
 * <p>
 * 
 * </p>
 */
    public Collection link_script_drug = new java.util.HashSet(); // of type link_script_drug
/**
 * <p>
 * 
 * </p>
 */
    public identity identity; 

    /** Holds value of property id. */
    private Long id;    

    /** Holds value of property qty. */
    private Double qty;
    
   ///////////////////////////////////////
   // access methods for associations

  
    
    /**
     *
     *@hibernate.set
     *  cascade="none"
     *@hibernate.collection-key
     *  column="link_script_drug"
     *@hibernate.collection-one-to-many
     *  class="org.gnumed.gmClinical.link_script_drug"
     */
    public Collection getLink_script_drugs() {
        return link_script_drug;
    }
    public void addLink_script_drug(link_script_drug _link_script_drug) {
        if (! this.link_script_drug.contains(_link_script_drug)) {
            this.link_script_drug.add(_link_script_drug);
            _link_script_drug.setScript_drug(this);
        }
    }
    public void removeLink_script_drug(link_script_drug _link_script_drug) {
        boolean removed = this.link_script_drug.remove(_link_script_drug);
        if (removed) _link_script_drug.setScript_drug((script_drug)null);
    }
    
      /** Setter for property link_script_drugs.
     * @param link_script_drugs New value of property link_script_drugs.
     *
     */
    public void setLink_script_drugs(Collection link_script_drugs) {
    link_script_drug = link_script_drugs;
    }
    
    /** 
     *
     *@hibernate.many-to-one
     */
    public identity getIdentity() {
        return identity;
    }
    public void setIdentity(identity _identity) {
        if (this.identity != _identity) {
            if (this.identity != null) this.identity.removeScript_drug(this);
            this.identity = _identity;
            if (_identity != null) _identity.addScript_drug(this);
        }
    }


  ///////////////////////////////////////
  // operations
    
     /**
     *
     *@hibernate.many-to-one
     */
    public package_size getPackage_size() {
        return package_size;
    }
    public void setPackage_size(package_size _package_size) {
        this.package_size = _package_size;
    }

/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public String getDirections() {        
        return directions;
    } // end getDirections        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setDirections(String _directions) {        
        directions = _directions;
    } // end setDirections        

/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public Double getDose_amount() {        
        return dose_amount;
    } // end getDose_amount        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setDose_amount(Double _dose_amount) {        
        dose_amount = _dose_amount;
    } // end setDose_amount        

/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public int getFrequency() {        
        return frequency;
    } // end getFrequency        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setFrequency(int _frequency) {        
        frequency = _frequency;
    } // end setFrequency        

/**
 * <p>
 * Represents ...
 * </p>
 *
 *@hibernate.property
 */
    public Boolean getPrn() {        
        return prn;
    } // end getPrn        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setPrn(Boolean _prn) {        
        prn = _prn;
    } // end setPrn        

/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public String getAdjuvant() {        
        return adjuvant;
    } // end getAdjuvant        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setAdjuvant(String _adjuvant) {        
        adjuvant = _adjuvant;
    }
    
    /** Getter for property current.
     * @return Value of property current.
     *
     *
     *@hibernate.property
     */
    public Boolean getCurrent() {
        return _current;
    }    
  
    /** Setter for property current.
     * @param current New value of property current.
     *
     */
    public void setCurrent(Boolean current) {
        _current = current;
    }
    
    /** Getter for property id.
     * @return Value of property id.
     *
     * @hibernate.id
     *  generator-class="hilo"
     */
    public Long getId() {
        return this.id;
    }
    
    /** Setter for property id.
     * @param id New value of property id.
     *
     */
    public void setId(Long id) {
        this.id = id;
    }
    
    /** Getter for property qty.
     * @return Value of property qty.
     * @hibernate.property
     */
    public Double getQty() {
        return this.qty;
    }
    
    /** Setter for property qty.
     * @param qty New value of property qty.
     *
     */
    public void setQty(Double qty) {
        this.qty = qty;
    }
    
 // end setAdjuvant        

} // end script_drug



