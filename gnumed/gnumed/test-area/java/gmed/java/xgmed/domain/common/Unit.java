/** Java class "Unit.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.common;

import java.util.*;

import xgmed.helper.Visitable;
import  xgmed.helper.Visitor; 
/**
 * <p>
 *  represents a Unit of measurement. An instance should be either AtomicUnit
 *  or a CompountUnit
 * 
 * </p>
 * @hibernate.class
 *  table="unit"
 *  discriminator-value="U"
 *@hibernate.discriminator
 *  column="type"
 *  type="string"
 *  length="2"
 */
public class Unit implements Visitable {

  ///////////////////////////////////////
  // attributes

 
/**
 * <p>
 * Represents ...
 * </p>
 */
    private String label; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Collection fromRatio = new java.util.HashSet(); // of type ConversionRatio
/**
 * <p>
 * 
 * </p>
 */
    public Collection toRatio = new java.util.HashSet(); // of type ConversionRatio
 /** Holds value of property id. */
    private Long id;    

    /** Getter for property id.
     * @return Value of property id.
     * @hibernate.id
     *  generator-class="hilo.long"
     *  type="long"
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

   ///////////////////////////////////////
   // access methods for associations

    public Collection getFromRatios() {
        return fromRatio;
    }
    
    public void addFromRatio(ConversionRatio conversionRatio) {
        if (! this.fromRatio.contains(conversionRatio)) {
            this.fromRatio.add(conversionRatio);
            conversionRatio.setToUnit(this);
        }
    }
    
    public void removeFromRatio(ConversionRatio conversionRatio) {
        boolean removed = this.fromRatio.remove(conversionRatio);
        if (removed) conversionRatio.setToUnit((Unit)null);
    }
    public Collection getToRatios() {
        return toRatio;
    }
    public void addToRatio(ConversionRatio conversionRatio) {
        if (! this.toRatio.contains(conversionRatio)) {
            this.toRatio.add(conversionRatio);
            conversionRatio.setFromUnit(this);
        }
    }
    public void removeToRatio(ConversionRatio conversionRatio) {
        boolean removed = this.toRatio.remove(conversionRatio);
        if (removed) conversionRatio.setFromUnit((Unit)null);
    }
/** Getter for property label.
     * @return Value of property label.
     * @hibernate.property
     */
    public String getLabel() {
        return this.label;
    }
    
    /** Setter for property label.
     * @param label New value of property label.
     *
     */
    public void setLabel(String label) {
        this.label = label;
    }
    
    /** Setter for property fromRatios.
     * @param fromRatios New value of property fromRatios.
     *
     */
    public void setFromRatios(Collection fromRatios) {
    fromRatio = fromRatios;
    }
    
    /** Setter for property toRatios.
     * @param toRatios New value of property toRatios.
     *
     */
    public void setToRatios(Collection toRatios) {
        toRatio = toRatios;
    }
    
    public void accept(Visitor v) {
        v.visitUnit(this);
    }
    
} // end Unit





