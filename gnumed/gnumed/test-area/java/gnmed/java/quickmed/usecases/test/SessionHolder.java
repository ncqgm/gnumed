/*
 * SessionHolder.java
 *
 * Created on 17 August 2003, 01:05
 */

package quickmed.usecases.test;
import net.sf.hibernate.*;
import gnmed.test.HibernateInit;
/**
 *
 * @author  syan
 */
public class SessionHolder {
    
    /** Holds value of property session. */
    private Session session;
    
    /** Creates a new instance of SessionHolder */
    public SessionHolder() {
    }
    
    /** Getter for property session; the session is re-connected if not
     * a new session.
     * @return Value of property session.
     *
     */
    public Session getSession() {
        if (session == null) {
            // this session is for getting objects for queries that are
            // not added into the identity object trees.
            
            try {
                session = HibernateInit.openSession();
                
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        if (!session.isConnected())
        try {
            session.reconnect();
            
        } catch (Exception e) {
            e.printStackTrace();
        }
        return this.session;
    }
    
    /** Setter for property session.
     * @param session New value of property session.
     *
     */
    public void setSession(Session session) {
        this.session = session;
        
        try {
            session.disconnect();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
}
