/** Java class "AtomicUnit.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.common;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 * @hibernate.subclass
 *  discriminator-value="A"
 */
public class AtomicUnit extends Unit {

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Collection compoundUnit = new java.util.HashSet(); // of type CompoundUnit
/**
 * <p>
 * 
 * </p>
 */
    public Collection inverseCompoundUnit = new java.util.HashSet(); // of type CompoundUnit


   ///////////////////////////////////////
   // access methods for associations
/**
     * see custom hbm files for many-to-many mappings.
     */
    public Collection getCompoundUnits() {
        return compoundUnit;
    }
    public void addCompoundUnit(CompoundUnit compoundUnit) {
        if (! this.compoundUnit.contains(compoundUnit)) {
            this.compoundUnit.add(compoundUnit);
            compoundUnit.addAtomicUnit(this);
        }
    }
    public void removeCompoundUnit(CompoundUnit compoundUnit) {
        boolean removed = this.compoundUnit.remove(compoundUnit);
        if (removed) compoundUnit.removeAtomicUnit(this);
    }
    
    /**
     * see custom hbm files for many-to-many mappings.
     */
    public Collection getInverseCompoundUnits() {
        return inverseCompoundUnit;
    }
    public void addInverseCompountUnit(CompoundUnit compoundUnit) {
        if (! this.inverseCompoundUnit.contains(compoundUnit)) {
            this.inverseCompoundUnit.add(compoundUnit);
            compoundUnit.addInverseUnit(this);
        }
    }
    public void removeInverseCompountUnit(CompoundUnit compoundUnit) {
        boolean removed = this.inverseCompoundUnit.remove(compoundUnit);
        if (removed) compoundUnit.removeInverseUnit(this);
    }

    /** Setter for property compoundUnits.
     * @param compoundUnits New value of property compoundUnits.
     *
     */
    public void setCompoundUnits(Collection compoundUnits) {
        compoundUnit = compoundUnits;
    }
    
    /** Setter for property inverseCompountUnits.
     * @param inverseCompountUnits New value of property inverseCompountUnits.
     *
     */
    public void setInverseCompoundUnits(Collection inverseCompoundUnits) {
        inverseCompoundUnit = inverseCompoundUnits;
    }
    
} // end AtomicUnit





