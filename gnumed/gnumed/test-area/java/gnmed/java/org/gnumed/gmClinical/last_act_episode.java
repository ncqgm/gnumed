/** Java class "last_act_episode.java" generated from Poseidon for UML.
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
public class last_act_episode {

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public clin_episode clin_episode; 

    /** Holds value of property id. */
    private Integer id;    

   ///////////////////////////////////////
   // access methods for associations
    
    
/**
 *@hibernate.many-to-one
 */
    public clin_episode getClin_episode() {
        return clin_episode;
    }
    public void setClin_episode(clin_episode _clin_episode) {
        if (this.clin_episode != _clin_episode) {
            this.clin_episode = _clin_episode;
            if (_clin_episode != null) _clin_episode.setLast_act_episode(this);
        }
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
    
} // end last_act_episode





