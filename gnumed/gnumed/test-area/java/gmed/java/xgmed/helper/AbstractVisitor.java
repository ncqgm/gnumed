/*
 * AbstractVisitor.java
 *
 * Created on 10 July 2003, 00:58
 */

package xgmed.helper;
import java.lang.reflect.Method;
import xgmed.domain.accountability.*;
import xgmed.domain.observation.*;
import xgmed.domain.common.*;
import java.util.*;

/**
 *
 * @author  syan
 */
public abstract class AbstractVisitor implements Visitor {
    
    abstract void nodeAction(Visitable v);
    /** Creates a new instance of AbstractVisitor */
    public AbstractVisitor() {
    }
     public void visitCategoryObservation(CategoryObservation v ) {
        v.getObservationConcept().accept(this);
        visitObservation(v);
    }
    
    public void visitIdentityObservation(IdentityObservation v ) {
        v.getCoding().accept(this);
        visitObservation(v);
    }
    
    public void visitMeasurement(Measurement v ) {
        if (v.getPhenomenonType() != null)
            v.getPhenomenonType().accept(this);
        v.getQuantity().accept(this);
        visitObservation(v);
        nodeAction(v);
    }
    
    public void visitPhenomenon(Phenomenon v ) {
        v.getPhenomenonType().accept(this);
        visitObservationConcept(v);
        nodeAction(v);
    }
    
    public void visitObservationConcept(ObservationConcept v) {
        if (v.getCoding() != null)
            v.getCoding().accept(this);
        nodeAction(v);
    }
    
    public void visitPhenomenonType(PhenomenonType v) {
        if (v.getCoding() != null)
            visitCoding(v.getCoding());
//        if (v.getUnit()  != null)
//            visitUnit(v.getUnit());
        nodeAction(v);
    }
    
    public void visitObservation(Observation v) {
        if (v.getApplicableTime() != null)
            v.getApplicableTime().accept(this);
        if (v.getRecordTime() != null)
            v.getRecordTime().accept(this);
        nodeAction(v);
    }
    
    public void visitCoding(Coding c) {
        nodeAction(c);
    }
    
    public void visitTimeRecord(TimeRecord r) {
        nodeAction(r);
    }
    
    public void visitTimePeriod(TimePeriod tp) {
        if (tp.getStart() != null)
            tp.getStart().accept(this);
        if (tp.getFinish() != null)
            tp.getFinish().accept(this);
    }
    
    public void visitTimepoint(Timepoint p) {
        nodeAction(p);
    }
    
    public void visitParty(Party party) {
        nodeAction(party.getAddress());
        visitVisitableCollection(party.getPartyTypes());
        visitVisitableCollection(party.getTelephones());
        visitVisitableCollection(party.getObservations());
        nodeAction(party);
    }
    
    protected void visitVisitableCollection(Collection c) {
        Iterator i = c.iterator();
        
        while (i.hasNext()) {
            Visitable v = (Visitable) i.next();
            v.accept(this);
        }
       
    }
    
    public void visitAddress(Address a) {
        nodeAction(a);
    }
    
    public void visitTelephone(Telephone t) {
        nodeAction(t);
    }
    
    public void visitPartyType(PartyType p) {
        nodeAction(p);
    }
    
    public void visitCompoundUnit(CompoundUnit u) {
        visitVisitableCollection(u.getAtomicUnits());
        visitVisitableCollection(u.getInverseUnits());
        nodeAction(u);
        
    }
    
    public void visitUnit(Unit u) {
        nodeAction(u);
    }
    
    public void visitQuantity(Quantity q) {
         if (q.getUnit() != null)
             q.getUnit().accept(this);
         nodeAction(q);
    }
    
    public void visitPerson(Person p) {
        nodeAction(p);
    }
    
}
