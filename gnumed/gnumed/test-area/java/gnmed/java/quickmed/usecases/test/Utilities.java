/*
 * Utilities.java
 *
 * Created on 19 August 2003, 21:26
 */

package quickmed.usecases.test;
import net.sf.hibernate.*;
import net.sf.hibernate.type.*;
import net.sf.hibernate.cfg.Configuration;
import java.lang.reflect.*;
import gnmed.test.HibernateInit;
import java.util.logging.*;
import java.util.*;
/**
 *
 * @author  syan
 */
public class Utilities {
    static Logger logger = Logger.global;
    
    /** Creates a new instance of Utilities */
    public Utilities() {
    }
    
    /** this method returns objects which should not have lazy collections, as the session no
     *longer exists to act as proxy cache.
     */
    public  static Object createOrFindEntity( String query,final  Object[] params, Type[] types,
    Class targetClass, Method[] paramSetters) throws Exception  {
        Session s = null;
        
        s = HibernateInit.openSession();
        Object o = createOrFindEntity(s, query, params, types,targetClass, paramSetters);
        HibernateInit.closeSession(s);
        return o;
    }
    
    
    /** finds or creates an entity , given the params; this method does not close the session it uses.
     */
    public  static Object createOrFindEntity(Session s, String query,final  Object[] params, Type[] types,
    Class targetClass, Method[] paramSetters) throws Exception  {
        if (!s.isConnected())
            s.reconnect();
        Object newObject = null;
        try {
           Iterator j  = s.iterate(query, params, types);
           if (j.hasNext())
               newObject = j.next();
            if (newObject != null) {
                return newObject;
            }
            throw new  Exception("No object found");
        } catch (Exception e) {
            try {
                logger.info("Unable to find a " + targetClass.getName() + " with specified parameters . CREATING NEW ONE");
                newObject = targetClass.newInstance();
                for (int i = 0; i < paramSetters.length; ++i) {
                    paramSetters[i].invoke(newObject, new Object[] { params[i] } );
                }
                s.save(newObject);
                s.flush();
                s.connection().commit();
                logger.fine("SUCCESSFULLY CREATED a " +  targetClass.getName() );
                return newObject;
            } catch ( Exception e2) {
                
               e2.printStackTrace();
                throw e2;
            }
        } finally {
            logger.info("DISCONNECTING   " + s.toString());
            //  s.disconnect();
            s.disconnect();
            
        }
        //        return newObject;
    }
}
