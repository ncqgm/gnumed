/** Java class "PartyType.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package  xgmed.domain.accountability;

import java.util.*;
import xgmed.helper.Visitable;
import  xgmed.helper.Visitor;
/**
 * <p>
 *
 * </p>
 * @hibernate.class
 *      table="party_type"
 */
public class PartyType implements Visitable {
    
    ///////////////////////////////////////
    // attributes
    
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    private Long id;
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    private String description;
    
    ///////////////////////////////////////
    // associations
    
    /**
     * <p>
     *
     * </p>
     */
    public Collection party = new java.util.HashSet(); // of type Party
    /**
     * <p>
     *
     * </p>
     */
    protected Collection commissioning = new java.util.HashSet(); // of type AccountabilityType
    /**
     * <p>
     *
     * </p>
     */
    protected Collection responsibility = new java.util.HashSet(); // of type AccountabilityType
    /**
     * <p>
     *
     * </p>
     */
    protected Collection superType = new java.util.HashSet(); // of type PartyType
    /**
     * <p>
     *
     * </p>
     */
    protected Collection subType = new java.util.HashSet(); // of type PartyType
    
    
    ///////////////////////////////////////
    // access methods for associations
    
    public Collection getPartys() {
        return party;
    }
    public void addParty(Party party) {
        if (! this.party.contains(party)) {
            this.party.add(party);
            party.addPartyType(this);
        }
    }
    public void removeParty(Party party) {
        boolean removed = this.party.remove(party);
        if (removed) party.removePartyType(this);
    }
    public Collection getCommissionings() {
        return commissioning;
    }
    public void addCommissioning(AccountabilityType accountabilityType) {
        if (! this.commissioning.contains(accountabilityType)) {
            this.commissioning.add(accountabilityType);
            accountabilityType.addCommissioner(this);
        }
    }
    public void removeCommissioning(AccountabilityType accountabilityType) {
        boolean removed = this.commissioning.remove(accountabilityType);
        if (removed) accountabilityType.removeCommissioner(this);
    }
    public Collection getResponsibilitys() {
        return responsibility;
    }
    public void addResponsibility(AccountabilityType accountabilityType) {
        if (! this.responsibility.contains(accountabilityType)) {
            this.responsibility.add(accountabilityType);
            accountabilityType.addResponsible(this);
        }
    }
    public void removeResponsibility(AccountabilityType accountabilityType) {
        boolean removed = this.responsibility.remove(accountabilityType);
        if (removed) accountabilityType.removeResponsible(this);
    }
    public Collection getSuperTypes() {
        return superType;
    }
    public void addSuperType(PartyType partyType) {
        if (! this.superType.contains(partyType)) {
            this.superType.add(partyType);
            partyType.addSubType(this);
        }
    }
    public void removeSuperType(PartyType partyType) {
        boolean removed = this.superType.remove(partyType);
        if (removed) partyType.removeSubType(this);
    }
    public Collection getSubTypes() {
        return subType;
    }
    public void addSubType(PartyType partyType) {
        if (! this.subType.contains(partyType)) {
            this.subType.add(partyType);
            partyType.addSuperType(this);
        }
    }
    public void removeSubType(PartyType partyType) {
        boolean removed = this.subType.remove(partyType);
        if (removed) partyType.removeSuperType(this);
    }
    
    
    ///////////////////////////////////////
    // operations
    
    
    /**
     * <p>
     * Represents ...
     * </p>
     * @hibernate.id
     *  generator-class="hilo.long"
     *  type="long"
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
    } // end setId
    
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
    }
    
    /** Setter for property partys.
     * @param partys New value of property partys.
     *
     */
    public void setPartys(Collection partys) {
    party = partys;
    }
    
    /** Setter for property responsibilitys.
     * @param responsibilitys New value of property responsibilitys.
     *
     */
    public void setResponsibilitys(Collection responsibilitys) {
    responsibility = responsibilitys;
    }
    
    /** Setter for property subTypes.
     * @param subTypes New value of property subTypes.
     *
     */
    public void setSubTypes(Collection subTypes) {
    subType = subTypes;
    }
    
    /** Setter for property superTypes.
     * @param superTypes New value of property superTypes.
     *
     */
    public void setSuperTypes(Collection superTypes) {
    superType = superTypes;
    }
    
    /** Setter for property commissionings.
     * @param commissionings New value of property commissionings.
     *
     */
    public void setCommissionings(Collection commissionings) {
    commissioning = commissionings;
    }
    
    public void accept(Visitor v) {
        v.visitPartyType(this);
    }
    
 // end setDescription
    
} // end PartyType





