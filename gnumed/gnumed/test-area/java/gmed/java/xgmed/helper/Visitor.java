/*
 * Visitor.java
 *
 * Created on 7 July 2003, 09:46
 */

package xgmed.helper;
import xgmed.domain.observation.*;
import xgmed.domain.common.*;
import xgmed.domain.accountability.*;
/**
 *
 * @author  sjtan
 */
public interface Visitor { 
    public void visitObservation(Observation v);
    public void visitIdentityObservation(IdentityObservation visitable) ;
    public void visitCategoryObservation(CategoryObservation visitable) ;
    public void visitPhenomenon(Phenomenon visitable);
    public void visitMeasurement(Measurement visitable);
    public void visitObservationConcept( ObservationConcept v);
    public void visitPhenomenonType( PhenomenonType v);
    public void visitCoding( Coding c);
    public void visitTimeRecord(TimeRecord r);
    public void visitTimepoint( Timepoint p);
    public void visitTimePeriod( TimePeriod tp);
    public void visitParty(Party party);
    public void visitPerson(Person p);
    public void visitTelephone(Telephone t);
    public void visitAddress(Address a);
    public void visitPartyType(PartyType p);
    public void visitUnit(Unit u);
    public void visitCompoundUnit(CompoundUnit u);
    public void visitQuantity(Quantity q);
}
