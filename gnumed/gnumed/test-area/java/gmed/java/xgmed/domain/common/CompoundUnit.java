/** Java class "CompoundUnit.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.common;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 * a compount unit
 * must have at least 
 * either
 * 1) one inverse unit
 * or 
 * 2)  two direct units
 *
 * @hibernate.subclass
 *  discriminator-value="A"
 */
public class CompoundUnit extends Unit {

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Collection atomicUnit = new java.util.HashSet(); // of type AtomicUnit
/**
 * <p>
 * 
 * </p>
 */
    public Collection inverseUnit = new java.util.HashSet(); // of type AtomicUnit


   ///////////////////////////////////////
   // access methods for associations

    /**
     * see custom hbm files for many-to-many mappings.
     */
    public Collection getAtomicUnits() {
        return atomicUnit;
    }
    public void addAtomicUnit(AtomicUnit atomicUnit) {
        if (! this.atomicUnit.contains(atomicUnit)) {
            this.atomicUnit.add(atomicUnit);
            atomicUnit.addCompoundUnit(this);
        }
    }
    public void removeAtomicUnit(AtomicUnit atomicUnit) {
        boolean removed = this.atomicUnit.remove(atomicUnit);
        if (removed) atomicUnit.removeCompoundUnit(this);
    }
    
    /**
     * see custom hbm files for many-to-many mappings.
     */
    public Collection getInverseUnits() {
        return inverseUnit;
    }
    public void addInverseUnit(AtomicUnit atomicUnit) {
        if (! this.inverseUnit.contains(atomicUnit)) {
            this.inverseUnit.add(atomicUnit);
            atomicUnit.addInverseCompountUnit(this);
        }
    }
    public void removeInverseUnit(AtomicUnit atomicUnit) {
        boolean removed = this.inverseUnit.remove(atomicUnit);
        if (removed) atomicUnit.removeInverseCompountUnit(this);
    }

    /** Setter for property atomicUnits.
     * @param atomicUnits New value of property atomicUnits.
     *
     */
    public void setAtomicUnits(Collection atomicUnits) {
    atomicUnit = atomicUnits;
    }
    
    /** Setter for property inverseUnits.
     * @param inverseUnits New value of property inverseUnits.
     *
     */
    public void setInverseUnits(Collection inverseUnits) {
    inverseUnit = inverseUnits;
    }
    
} // end CompoundUnit





