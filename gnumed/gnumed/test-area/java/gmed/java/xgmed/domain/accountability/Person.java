/** Java class "Person.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.accountability;
import xgmed.helper.Visitor;
import java.util.*;
import java.util.Date;

/**
 * <p>
 * 
 * </p>
 * @hibernate.subclass
 *  discriminator-value="P"
 */
public class Person extends Party {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private String firstNames; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String lastNames; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private Date birthdate; 

    /** Holds value of property male. */
    private boolean male;
    
  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public String getLastNames() {        
        return lastNames;
    } // end getLastNames        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setLastNames(String _lastNames) {        
        lastNames = _lastNames;
    } // end setLastNames        

/**
 * <p>
 * Represents ...
 * @hibernate.property
 */
    public String getFirstNames() {        
        return firstNames;
    } // end getFirstNames        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setFirstNames(String _firstNames) {        
        firstNames = _firstNames;
    } // end setFirstNames        

/**
 * <p>
 * Represents ...
 * @hibernate.property
 */
    public Date getBirthdate() {        
        return birthdate;
    } // end getBirthdate        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setBirthdate(Date _birthdate) {        
        birthdate = _birthdate;
    }
    
    /** Getter for property male.
     * @return Value of property male.
     *
     */
    public boolean isMale() {
        return this.male;
    }
    
    /** Setter for property male.
     * @param male New value of property male.
     *
     */
    public void setMale(boolean male) {
        this.male = male;
    }
    
 // end setBirthdate        
    
    public void accept(Visitor v) {
        v.visitPerson(this);   
    }

} // end Person





