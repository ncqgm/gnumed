/** Java class "Telephone.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.accountability;

import java.util.*;

import xgmed.helper.Visitable;
import xgmed.helper.Visitor;

/**
 * <p>
 * 
 * </p>
 * @hibernate.class
 *  table="telephone"
 */
public class Telephone implements Visitable {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private String number; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Collection party = new java.util.HashSet();
    
    /** Holds value of property id. */
    private Long id;
    
 // of type Party


   ///////////////////////////////////////
   // access methods for associations

    public Collection getPartys() {
        return party;
    }
    
    public void setPartys(Collection c) {
        party = c;
    }
    
    public void addParty(Party party) {
        if (! this.party.contains(party)) {
            this.party.add(party);
            party.addTelephone(this);
        }
    }
    public void removeParty(Party party) {
        boolean removed = this.party.remove(party);
        if (removed) party.removeTelephone(this);
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public String getNumber() {        
        return number;
    } // end getNumber        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setNumber(String _number) {        
        number = _number;
    }
    
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
    
    public void accept(Visitor v) {
        v.visitTelephone(this);
    }
    
 // end setNumber        

} // end Telephone





