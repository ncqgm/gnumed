/** Java class "TimePeriod.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.common;

import java.util.*;
import xgmed.domain.accountability.Accountability;


import xgmed.helper.Visitable;
import  xgmed.helper.Visitor; 
/**
 * <p>
 *
 * </p>
 * @hibernate.subclass
 *  discriminator-value="P"
 */
public class TimePeriod extends TimeRecord {
    
    ///////////////////////////////////////
    // associations
    /**
     * <p>
     *
     * </p>
     */
    private  Timepoint start;
    
    /** Holds value of property finish. */
    private Timepoint finish;
    /**
     * <p>
     *
     * </p>
     */
    public Collection accountability = new java.util.HashSet();
    
    /** Holds value of property indefinite. */
    private Boolean indefinite;    
    
    
    // of type Accountability
    
    
    ///////////////////////////////////////
    // access methods for associations
    
    /**
     * @hibernate.many-to-one
     *  cascade="all"
     */
    public Timepoint getStart() {
        return start;
    }
    public void setStart(Timepoint timepoint) {
        this.start = timepoint;
    }
    
    /**
     *@hibernate.collection-one-to-many
     *  class="xgmed.domain.accountability.Accountability"
     */
    public Collection getAccountabilitys() {
        return accountability;
    }
    public void addAccountability(Accountability accountability) {
        if (! this.accountability.contains(accountability)) {
            this.accountability.add(accountability);
            accountability.setTimePeriod(this);
        }
    }
    public void removeAccountability(Accountability accountability) {
        boolean removed = this.accountability.remove(accountability);
        if (removed) accountability.setTimePeriod((TimePeriod)null);
    }
    
    /** Setter for property accountabilitys.
     * @param accountabilitys New value of property accountabilitys.
     *
     */
    public void setAccountabilitys(Collection accountabilitys) {
        accountability = accountabilitys;
    }
    
    /** Getter for property finish.
     * @return Value of property finish.
     *
     * @hibernate.many-to-one
     *  cascade="all"
     */
    public Timepoint getFinish() {
        return this.finish;
    }
    
    /** Setter for property finish.
     * @param finish New value of property finish.
     *
     */
    public void setFinish(Timepoint finish) {
        this.finish = finish;
    }
    
    public double getDays() {
	    return (double) 2.0;
    }
    
    /** Getter for property indefinite.
     * @return Value of property indefinite.
     *
     * @hibernate.property
     */
    public Boolean getIndefinite() {
        return this.indefinite;
    }
    
    /** Setter for property indefinite.
     * @param indefinite New value of property indefinite.
     *
     */
    public void setIndefinite(Boolean indefinite) {
        this.indefinite = indefinite;
    }
    
    public void accept(Visitor v) {
        v.visitTimePeriod(this);
    }
    
} // end TimePeriod





