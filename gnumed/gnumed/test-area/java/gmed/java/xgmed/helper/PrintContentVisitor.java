/*
 * PrintContentVisitor.java
 *
 * Created on 11 July 2003, 02:54
 */

package xgmed.helper;

import java.util.*;
import xgmed.domain.accountability.*;
import xgmed.domain.observation.*;
import xgmed.domain.common.*;
/**
 * visits nodes and prints their contents.
 * @author  sjtan
 */
public class PrintContentVisitor extends AbstractVisitor implements Visitor {
    static  java.text.NumberFormat dformat;
    static {
        dformat = java.text.NumberFormat.getInstance();
        dformat.setMaximumFractionDigits(2);
    };
    /** Holds value of property output. */
    private java.io.PrintStream output = System.out;
    
    void nodeAction(Visitable v) {
        getOutput().println(v);
    }
    
    public void visitAddress(Address a) {
        getOutput().println( a.getStreet() + " " + a.getSuburb() + " "+a.getPostcode() );
    }
    
    public void visitCategoryObservation(CategoryObservation visitable) {
        getOutput().print("observation of ");
        visitable.getObservationConcept().accept(this);
        getOutput().print(", ");
        visitObservation( visitable );
    }
    
    public void visitCoding(Coding c) {
        
        getOutput().print(c.getCodeScheme().getDescription());
        getOutput().print(" id = ");
        getOutput().print( c.getCode() );
    }
    
    public void visitIdentityObservation(IdentityObservation visitable) {
        getOutput().print("identity of ");
        if (visitable.getCoding() != null)
            visitable.getCoding().accept(this);
        getOutput().print(", ");
        visitObservationConcept(visitable.getObservationConcept());
        getOutput().println();
    }
    
    public void visitMeasurement(Measurement visitable) {
        getOutput().print("Measurement of ");
        if (visitable.getPhenomenonType() != null)
            visitable.getPhenomenonType().accept(this);
        getOutput().print(" ");
        if (visitable.getQuantity()!=null)
            visitable.getQuantity().accept(this);
        getOutput().println();
    }
    
    public void visitObservation(Observation v) {
        if (v.getApplicableTime() != null) {
            getOutput().print("Applicable ");
            v.getApplicableTime().accept(this);
        }
        if (v.getRecordTime() != null) {
            getOutput().print("Recorded ");
            v.getRecordTime().accept(this);
        }
        getOutput().println();
    }
    
    public void visitObservationConcept(ObservationConcept v) {
        getOutput().print(" concept:" + v.getDescription());
    }
    
    public void visitParty(Party party) {
        visitVisitableCollection(party.getTelephones());
        visitVisitableCollection(party.getPartyTypes());
        visitVisitableCollection(party.getObservations());
    }
    
    public void visitPartyType(PartyType p) {
        getOutput().print("Party Type of ");
        getOutput().print(p.getDescription());
        getOutput().println();
    }
    
    public void visitPhenomenon(Phenomenon visitable) {
        getOutput().print(visitable.getDescription());
        getOutput().print(" of type ");
        visitPhenomenonType(visitable.getPhenomenonType());
        getOutput().println();
    }
    
    public void visitPhenomenonType(PhenomenonType v) {
        getOutput().print(v.getDescription());
    }
    
    public void visitTelephone(Telephone t) {
        getOutput().print("Telephone:");
        getOutput().print(t.getNumber());
        getOutput().println();
        
    }
    
    public void visitTimePeriod(TimePeriod tp) {
        if (tp.getStart() != null) {
            getOutput().print("Start:");
            tp.getStart().accept(this);
        }
        if (tp.getFinish() != null) {
            getOutput().print(" Finish:");
            tp.getFinish().accept(this);
        }
        if (tp.getIndefinite() != null && tp.getIndefinite().booleanValue()) {
            getOutput().print(" is indefinite. ");
        }
        
    }
    
    public void visitTimeRecord(TimeRecord r) {
        
    }
    
    public void visitTimepoint(Timepoint p) {
        getOutput().print("Time = ");
        getOutput().print(p.getTimeValue()  );
        getOutput().print(" ");
    }
    
    public void visitPerson(Person p) {
        getOutput().println(p.getFirstNames() + " " + p.getLastNames());
        visitParty(p);
        getOutput().println();
    }
    
    public void visitVisitableCollection( Collection c, String delim) {
        Iterator i = c.iterator();
        
        for (int j = 0; i.hasNext() ; ++j) {
            Visitable v = (Visitable) i.next();
            v.accept(this);
            if ( j < c.size() -1 )
                getOutput().print(delim);
        }
    }
    
    public void visitCompoundUnit(CompoundUnit u) {
        if (u == null)
            return;
        visitVisitableCollection(u.getAtomicUnits(), ".");
        if (u.getInverseUnits() != null && u.getInverseUnits().size() != 0)
            getOutput().print("/");
        
        visitVisitableCollection(u.getInverseUnits(), "/");
    }
    
    public void visitUnit(Unit u) {
        if (u == null)
            return;
        getOutput().print(u.getLabel());
    }
    
    public void visitQuantity(Quantity q) {
        //        getOutput().print("qty=");
        
        getOutput().print(dformat.format(q.getNumber()));
        
        if (q.getUnit() != null)
            q.getUnit().accept(this);
    }
    /** Getter for property output.
     * @return Value of property output.
     *
     */
    public java.io.PrintStream getOutput() {
        return this.output;
    }
    
    /** Setter for property output.
     * @param output New value of property output.
     *
     */
    public void setOutput(java.io.PrintStream output) {
        this.output = output;
    }
    
}
