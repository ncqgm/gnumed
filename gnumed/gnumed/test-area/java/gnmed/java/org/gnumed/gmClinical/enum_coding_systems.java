/** Java class "enum_coding_systems.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package  org.gnumed.gmClinical;

import java.util.*;

/**
 * <p>
 * 
 * </p>
  * @hibernate.class
 */
public class enum_coding_systems {

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Collection coding_systems = new java.util.HashSet();
    
    /** Holds value of property id. */
    private Integer id;
    
 // of type coding_systems


   ///////////////////////////////////////
   // access methods for associations

    public Collection getCoding_systemss() {
        return coding_systems;
    }
    /** Setter for property coding_systemss.
     * @param coding_systemss New value of property coding_systemss.
     *
     */
    public void setCoding_systemss(Collection coding_systemss) {
    coding_systems = coding_systemss;
    }
    public void addCoding_systems(coding_systems _coding_systems) {
        if (! this.coding_systems.contains(_coding_systems)) {
            this.coding_systems.add(_coding_systems);
            _coding_systems.setEnum_coding_systems(this);
        }
    }
    public void removeCoding_systems(coding_systems _coding_systems) {
        boolean removed = this.coding_systems.remove(_coding_systems);
        if (removed) _coding_systems.setEnum_coding_systems((enum_coding_systems)null);
    }

    /** Getter for property id.
     * @return Value of property id.
       * @hibernate.id
     *  generator-class="hilo"
     */
    public Integer getId() {
        return this.id;
    }    
   
    /** Setter for property id.
     * @param id New value of property id.
     *
     */
    public void setId(Integer id) {
        this.id = id;
    }    
    
} // end enum_coding_systems





