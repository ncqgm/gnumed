/*
 * IdentityManager.java
 *
 * Created on 5 August 2003, 11:02
 */

package quickmed.usecases.test;
import java.util.*;
import java.util.logging.*;

import net.sf.hibernate.*;
import net.sf.hibernate.type.*;
import junit.framework.*;


import org.drugref.*;
import org.gnumed.gmIdentity.*;
import org.gnumed.gmClinical.*;

import java.lang.reflect.*;

import gnmed.test.HibernateInit;
/**
 *
 * @author  sjtan
 */
public class IdentityManager {
    static Logger logger = Logger.global;
    static IdentityManager manager;
    
    static {
        manager = new IdentityManager();
    }
    
    public static IdentityManager instance() {
        return manager;
    }
    
    /** Creates a new instance of IdentityManager */
    IdentityManager() {
       
    }
    
    public void save(identity id ) throws Exception  {
        Session sess = getSession();
       
        if (id .getId() == null) {
            sess.save(id );
            Logger.global.fine("SAVED NEW ID ");
            
        }
        else
            sess.update(id );
        sess.flush();
        sess.connection().commit();
        sess.disconnect();
        
    }
    
    public List findIdentityByNames( String lastnames, String firstnames) throws Exception {
        //         Session sess =  gnmed.test.HibernateInit.openSession();
        Session sess = getSession();
        
        List l = sess.find("select i from identity i inner join i.namess n " +
        "where lower(n.lastnames) like ? and lower(n.firstnames) like ?" ,
        new Object[] { lastnames.toLowerCase()+"%", firstnames.toLowerCase() +"%" },
        new Type[] { Hibernate.STRING , Hibernate.STRING } );
        
        //       gnmed.test.HibernateInit.closeSession(sess);
        sess.disconnect();
        return l;
    }
    
   public  static Object createOrFindEntity( String query,final  Object[] params, Type[] types,
    Class targetClass, Method[] paramSetters) throws Exception  {
        Object newObject = null;
        Session s = null;
        try {
            s=  HibernateInit.openSession();
            newObject = s.iterate(query, params, types).next();
            if (newObject != null) {
                return newObject;
            }
            throw new  Exception("No object found");
        } catch (Exception e) {
            try {
                logger.fine("Unable to find a " + targetClass.getName() + " with specified parameters . CREATING NEW ONE");
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
                
                HibernateInit.closeSession(s);
                throw e2;
            }
        } finally {
            logger.fine("DISCONNECTING AND CLOSING " + s.toString());
            //  s.disconnect();
            HibernateInit.closeSession(s);
            
        }
        //        return newObject;
    }
    
    private SessionHolder sessionHolder = new SessionHolder();
    /** Getter for property session.
     * @return Value of property session.
     *
     */
    public Session getSession() {
       return getSessionHolder().getSession();
    }
    
    /** Setter for property session.
     * @param session New value of property session.
     *
     */
    public void setSession(Session session) {
        getSessionHolder().setSession(session);
    }
    
    /** Getter for property sessionHolder.
     * @return Value of property sessionHolder.
     *
     */
    public SessionHolder getSessionHolder() {
        return this.sessionHolder;
    }
    
    /** Setter for property sessionHolder.
     * @param sessionHolder New value of property sessionHolder.
     *
     */
    public void setSessionHolder(SessionHolder sessionHolder) {
        this.sessionHolder = sessionHolder;
    }
    
}
