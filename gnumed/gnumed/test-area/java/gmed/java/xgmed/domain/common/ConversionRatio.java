/** Java class "ConversionRatio.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.common;

import java.util.*;

/**
 * <p>
 *
 * </p>
 * @hibernate.class
 *  table="conversion_ratio"
 */
public class ConversionRatio {
    
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
    private Double number;
    
    ///////////////////////////////////////
    // associations
    
    /**
     * <p>
     *
     * </p>
     */
    public Unit toUnit;
    /**
     * <p>
     *
     * </p>
     */
    public Unit fromUnit;
    
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
    
    
    /**
     * the unit converting to.
     *  @hibernate.many-to-one
     */
    public Unit getToUnit() {
        return toUnit;
    }
    
    public void setToUnit(Unit unit) {
        if (this.toUnit != unit) {
            if (this.toUnit != null) this.toUnit.removeFromRatio(this);
            this.toUnit = unit;
            if (unit != null) unit.addFromRatio(this);
        }
    }
    
    /**
     * the unit converting from.
     *  @hibernate.many-to-one
     */
    public Unit getFromUnit() {
        return fromUnit;
    }
    
    public void setFromUnit(Unit unit) {
        if (this.fromUnit != unit) {
            if (this.fromUnit != null) this.fromUnit.removeToRatio(this);
            this.fromUnit = unit;
            if (unit != null) unit.addToRatio(this);
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
    
    /**
     * <p>
     * Represents ...
     * </p>
     * @hibernate.property
     */
    public Double getNumber() {
        return number;
    } // end getNumber
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    public void setNumber(Double _number) {
        number = _number;
    } // end setNumber
    
} // end ConversionRatio





