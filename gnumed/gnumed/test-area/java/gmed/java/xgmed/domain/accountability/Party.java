/** Java class "Party.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package  xgmed.domain.accountability;

import java.util.*;
import xgmed.domain.observation.Observation;
import xgmed.domain.planning.resource.Asset;

import xgmed.helper.Visitable;
import xgmed.helper.Visitor;

/**
 * <p>
 *
 * </p>
 * @hibernate.class
 *  table="party"
 *  discriminator-value="Y"
 * @hibernate.discriminator
 *      column="type"
 *      type="string"
 *      length="2"
 */
public class Party    implements Visitable {
    
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
    private String name;
    
    ///////////////////////////////////////
    // associations
    
    /**
     * <p>
     *
     * </p>
     */
    public Address address;
    /**
     * <p>
     *
     * </p>
     */
    public Collection telephone = new java.util.HashSet(); // of type Telephone
    /**
     * <p>
     *
     * </p>
     */
    public Collection observation = new java.util.HashSet(); // of type Observation
    /**
     * <p>
     *
     * </p>
     */
    public Collection requirement = new java.util.HashSet(); // of type Accountability
    /**
     * <p>
     *
     * </p>
     */
    public Collection responsibility = new java.util.HashSet(); // of type Accountability
    /**
     * <p>
     *
     * </p>
     */
    protected Collection partyType = new java.util.HashSet(); // of type PartyType
    
    
    ///////////////////////////////////////
    // access methods for associations
    
    /**
     *@hibernate.many-to-one
     */
    public Address getAddress() {
        return address;
    }
    public void setAddress(Address address) {
        if (this.address != address) {
            if (this.address != null) this.address.removeParty(this);
            this.address = address;
            if (address != null) address.addParty(this);
        }
    }
    
    
    public Collection getTelephones() {
        return telephone;
    }
    public void addTelephone(Telephone telephone) {
        if (! this.telephone.contains(telephone)) {
            this.telephone.add(telephone);
            telephone.addParty(this);
        }
    }
    public void removeTelephone(Telephone telephone) {
        boolean removed = this.telephone.remove(telephone);
        if (removed) telephone.removeParty(this);
    }
    public Collection getObservations() {
        return observation;
    }
    public void addObservation(Observation observation) {
        if (! this.observation.contains(observation)) {
            this.observation.add(observation);
            observation.setSubject(this);
        }
    }
    public void removeObservation(Observation observation) {
        boolean removed = this.observation.remove(observation);
        if (removed) observation.setSubject((Party)null);
    }
    public Collection getRequirements() {
        return requirement;
    }
    public void addRequirement(Accountability accountability) {
        if (! this.requirement.contains(accountability)) {
            this.requirement.add(accountability);
            accountability.setCommissioner(this);
        }
    }
    public void removeRequirement(Accountability accountability) {
        boolean removed = this.requirement.remove(accountability);
        if (removed) accountability.setCommissioner((Party)null);
    }
    public Collection getResponsibilitys() {
        return responsibility;
    }
    public void addResponsibility(Accountability accountability) {
        if (! this.responsibility.contains(accountability)) {
            this.responsibility.add(accountability);
            accountability.setResponsible(this);
        }
    }
    public void removeResponsibility(Accountability accountability) {
        boolean removed = this.responsibility.remove(accountability);
        if (removed) accountability.setResponsible((Party)null);
    }
    public Collection getPartyTypes() {
        return partyType;
    }
    public void addPartyType(PartyType partyType) {
        if (! this.partyType.contains(partyType)) {
            this.partyType.add(partyType);
            partyType.addParty(this);
        }
    }
    public void removePartyType(PartyType partyType) {
        boolean removed = this.partyType.remove(partyType);
        if (removed) partyType.removeParty(this);
    }
    
    
    ///////////////////////////////////////
    // operations
    
    
    //
    /**
     * <p>
     * Represents ...
     * </p>
     * @hibernate.property
     */
    public String getName() {
        return name;
    } // end getName
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    public void setName(String _name) {
        name = _name;
    }
    
    /** Setter for property observations.
     * @param observations New value of property observations.
     *
     */
    public void setObservations(Collection observations) {
        observation = observations;
    }
    
    /** Setter for property partyTypes.
     * @param partyTypes New value of property partyTypes.
     *
     */
    public void setPartyTypes(Collection partyTypes) {
        partyType = partyTypes;
    }
    
    /** Setter for property requirements.
     * @param requirements New value of property requirements.
     *
     */
    public void setRequirements(Collection requirements) {
        requirement = requirements;
    }
    
    /** Setter for property responsibilitys.
     * @param responsibilitys New value of property responsibilitys.
     *
     */
    public void setResponsibilitys(Collection responsibilitys) {
        responsibility = responsibilitys;
    }
    
    /** Setter for property telephones.
     * @param telephones New value of property telephones.
     *
     */
    public void setTelephones(Collection telephones) {
        telephone = telephones;
    }
    
    /** Getter for property id.
     * @return Value of property id.
     * @hibernate.id
     *      generator-class="hilo.long"
     *      type="long"
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
        v.visitParty(this);
    }    
    
    // end setName
    
} // end Party





