/** Java class "PhenomenonType.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.observation;

import java.util.*;
import xgmed.domain.common.*;

import xgmed.helper.Visitable;
import xgmed.helper.Visitor;
/**
 * <p>
 * </p>
 * @hibernate.class
 *  table="phenomenon_type"
 */
public class PhenomenonType implements Visitable {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private String description; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private Long id; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Collection phenomenon = new java.util.HashSet(); // of type Phenomenon
/**
 * <p>
 * 
 * </p>
 */
    public Coding coding; 

     public Unit unit; 


   ///////////////////////////////////////
   // access methods for associations

    
     
     /**
      *@hibernate.many-to-one
      */
    public Unit getUnit() {
        return unit;
    }
    public void setUnit(Unit unit) {
        this.unit = unit;
    }
    
    /**
     *@hibernate.one-to-many
     */
    public Collection getPhenomenons() {
        return phenomenon;
    }
    public void addPhenomenon(Phenomenon phenomenon) {
        if (! this.phenomenon.contains(phenomenon)) {
            this.phenomenon.add(phenomenon);
            phenomenon.setPhenomenonType(this);
        }
    }
    public void removePhenomenon(Phenomenon phenomenon) {
        boolean removed = this.phenomenon.remove(phenomenon);
        if (removed) phenomenon.setPhenomenonType((PhenomenonType)null);
    }
   
     /** Setter for property phenomenons.
     * @param phenomenons New value of property phenomenons.
     *
     */
    public void setPhenomenons(Collection phenomenons) {
        phenomenon = phenomenons;
    }
   
    
    /**
     *@hibernate.one-to-one
     */
    public Coding getCoding() {
        return coding;
    }
    public void setCoding(Coding coding) {
        if (this.coding != coding) {
            this.coding = coding;
            if (coding != null) coding.setPhenomenonType(this);
        }
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public String getDescription() {        
        return description;
    } // end getDescription        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setDescription(String _description) {        
        description = _description;
    } // end setDescription        

 // end getCode        

 // end setCode        

/**
 * <p>
 * Represents ...
 * </p>
 *@hibernate.id
 *  generator-class="hilo.long"
 *      type="long"
 */
    public Long getId() {        
        return id;
    } // end getId        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setId(Long _id) {        
        id = _id;
    }
    
   
    public void accept(Visitor v) {
        v.visitPhenomenonType(this);
    }
    
 // end setId        

} // end PhenomenonType





