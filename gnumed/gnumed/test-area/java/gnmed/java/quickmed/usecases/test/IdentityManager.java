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
    
    static Map mapMarital ;
    public  static category_type maritalStatus = createOrFindCategoryType( Globals.bundle.getString("marital_status") );
    
    public  static category_type ABO = createOrFindCategoryType( Globals.bundle.getString("ABO") );
    
    
    public  static category_type rhesus = createOrFindCategoryType( Globals.bundle.getString("rhesus") );
    
    public final static int MEDICARE_ID = 1;
    public final static int PENSION_ID = 2;
    public final static int RECORD_NO_ID = 3;
    public final static int PROVIDER_ID = 5;
    public final static int PRESCRIBER_ID = 7;
    
    public final static enum_social_id pension = createOrFindEnumSocialId(Globals.bundle.getString("pension") , PENSION_ID);
    public final static enum_social_id medicare =createOrFindEnumSocialId(Globals.bundle.getString("medicare"), MEDICARE_ID);
    public final static enum_social_id recordNo = createOrFindEnumSocialId(Globals.bundle.getString("record_no"), RECORD_NO_ID);
    public final static enum_social_id providerNo = IdentityManager.createOrFindEnumSocialId(Globals.bundle.getString("provider_no"), PROVIDER_ID);
    public final static enum_social_id prescriberNo = IdentityManager.createOrFindEnumSocialId(Globals.bundle.getString("prescriber_no"), PRESCRIBER_ID);
  
    
    public final static category married = createOrFindCategory( Globals.bundle.getString("married"), maritalStatus);
    public final static  category unmarried = createOrFindCategory( Globals.bundle.getString("unmarried"), maritalStatus);
    public final static    category divorced = createOrFindCategory( Globals.bundle.getString("divorced"), maritalStatus);
    public final static   category widowed = createOrFindCategory( Globals.bundle.getString("widowed"), maritalStatus);
    public final static category unknown = createOrFindCategory( Globals.bundle.getString("unknown"), maritalStatus);
    public final static category [] maritalList = new category[] { married, unmarried, divorced, widowed };
    
    
    public final static category A = createOrFindCategory( Globals.bundle.getString("A"), ABO);
    public final static  category B = createOrFindCategory( Globals.bundle.getString("B"), ABO);
    public  final static    category AB = createOrFindCategory( Globals.bundle.getString("AB"), ABO);
    public final static   category O = createOrFindCategory( Globals.bundle.getString("O"), ABO);
    public final static category rhPos = createOrFindCategory( Globals.bundle.getString("positive"), rhesus);
    public final static category rhNeg = createOrFindCategory( Globals.bundle.getString("negative"), rhesus);
    public final static category [] ABOList = new category[] {A, B, AB, O };
    public final static category [] rhesusList = new category[] {rhPos, rhNeg };
    
    static category_type createAndSaveCategoryType  (Session sess, String type) throws Exception {
        category_type c = new category_type();
        c.setName(type);
        sess.save(c);
        sess.flush();
        sess.connection().commit();
        logger.fine("SAVED CATEGORY_TYPE = " + c.getId() + " " +c.getName());
        return c;
    }
    
    public static category_type createOrFindCategoryType(String type) {
        category_type c = null;
        Session sess = null;
        try {
            sess =  HibernateInit.openSession();
            List l = sess.find("select ct from category_type ct where ct.name like ?",
            type,  Hibernate.STRING
            );
            
            if (l.size() == 0 )
                c = createAndSaveCategoryType(sess,   type);
            else
                c = (category_type) l.get(0);
        } catch (Exception e) {
            
            e.printStackTrace();
            
        }finally {
            try {
                HibernateInit.closeSession(sess);
            }
            catch (Exception e2) {
                e2.printStackTrace();
            }
        }
        return c;
    }
    
    static category createAndSaveCategory( Session sess, String type, category_type superType )throws Exception {
        category c = new category();
        c.setName(type);
        c.setCategory_type(superType);
        sess.save(c);
        sess.flush();
        
        sess.connection().commit();
        return c;
    }
    
    public static category createOrFindCategory(String type, category_type superType) {
        category c = null;
        Session sess = null;
        try {
            sess =  HibernateInit.openSession();
            List l = sess.find("select c from category c where c.name like ? and c.category_type.id = ?",
            new Object[] { type, superType.getId() } ,
            new Type[] { Hibernate.STRING, Hibernate.LONG }
            );
            
            if (l.size() == 0 )
                c = createAndSaveCategory(sess,   type, superType);
            else
                c = (category) l.get(0);
        } catch (Exception e) {
            
            e.printStackTrace();
            
        }finally {
            try {
                HibernateInit.closeSession(sess);
            }
            catch (Exception e2) {
                e2.printStackTrace();
            }
        }
        return c;
    }
    
    
    
    public static enum_social_id createOrFindEnumSocialId(String name, int id) {
        
        try {
            final  Method[] socialIdSetters = new Method[] {
                enum_social_id.class.getMethod("setName",
                new Class[] { String.class}),
                enum_social_id.class.getMethod("setId", new Class[]{ Integer.class}) };
                
                return (enum_social_id) Utilities.createOrFindEntity(
                "from e in class org.gnumed.gmIdentity.enum_social_id where e.name = ? and  e.id = ?",
                new Object[] { name, new Integer(id) },
                new Type[] { Hibernate.STRING, Hibernate.INTEGER },
                enum_social_id.class , socialIdSetters
                
                );
        } catch (Exception e ) {
            e.printStackTrace();
        }
        enum_social_id eid = new enum_social_id();
        eid.setName(name);
        eid.setId(new Integer(id));
        return eid;
    }
    
    
    
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
    
    public void delete( identity id) throws Exception {
        Session sess = getSession();
        if (id.getId() != null) {
            sess.delete(id);
            sess.flush();
            sess.connection().commit();
            sess.disconnect();
        }
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
    
    public Iterator getIteratorIdentityByNames( String lastnames, String firstnames) throws Exception {
        //         Session sess =  gnmed.test.HibernateInit.openSession();
        Session sess = getSession();
        return getIteratorIdentityByNames( sess,  lastnames,  firstnames);
    }
    
    public Iterator getIteratorIdentityByNames(Session sess, String lastnames, String firstnames) throws Exception {
   
        return  sess.iterate("select i from search_identity i inner join i.namess n " +
        "where lower(n.lastnames) like ? and lower(n.firstnames) like ?" ,
        new Object[] { lastnames.toLowerCase()+"%", firstnames.toLowerCase() +"%" },
        new Type[] { Hibernate.STRING , Hibernate.STRING } );
         
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
    
    
    public identity_role createOrFindRole( String name) {
        try {
            return (identity_role)
            Utilities.createOrFindEntity(getSession(), "select r from identity_role r where r.name like ?",
            new Object[] { name }, new Type[] { Hibernate.STRING },
            identity_role.class,
            new Method[] { identity_role.class.getMethod("setName" , new Class[] { String.class } ) } );
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
    
    public void updateRole( identity_role role) {
        try {
            getSession().update(role);
            getSession().flush();
            getSession().connection().commit();
            getSession().disconnect();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    final static Type[] twoStringTypes =  new Type[] {Hibernate.STRING  , Hibernate.STRING } ;
    
    /** finds providers given names or roles. If no roles are given a name search should be done.
     */
    public List findProviders( String last, String first, identity_role[] roles) throws Exception {
        FlushMode oldMode =  getSession().getFlushMode();
        try {
            //            getSession().setFlushMode(FlushMode.AUTO);
            if (last == null)
                last = "";
            if (first == null)
                first = "";
            last = last.trim().toLowerCase();
            first = first.trim().toLowerCase();
            
            String query = "select i from identity i inner join i.roles r "+
            "where r.identity_role.name  like ? ";
            
            String query2 = "select i from identity i inner join i.roles r inner join i.namess n "+
            "where lower(n.lastnames) like ? and lower(n.firstnames) like ? ";
            
            Set set = new HashSet();
            if ( roles.length == 0  ) {
                set.addAll(getSession().find(query2, new Object[] { last+"%", first+"%" },
                twoStringTypes ) );
            }
            
            
            for (int i = 0; i < roles.length; ++i) {
                
                List l = getSession().find(query,   roles[i].getName()  , Hibernate.STRING  ) ;
                
                if (last.length() > 0) {
                    Collection c = new ArrayList();
                    Iterator j = l.iterator();
                    while (j.hasNext()) {
                        identity id = (identity) j.next();
                        if (id.findNames(0).getLastnames().toLowerCase().startsWith(last) &&
                        id.findNames(0).getLastnames().toLowerCase().startsWith(first) )
                            c.add(id);
                    }
                    
                    //                    getSession().update(l);
                    //                    getSession().connection().commit();
                    //                    Collection c = getSession().filter( l, query2, new Object[] { last+"%", first+"%" },
                    //                    twoStringTypes ) ;
                    set.addAll(c);
                    continue;
                }
                set.addAll(l);
            }
            
            
            // more stuff get a good test string
            
            return Arrays.asList(set.toArray());
        } finally {
            getSession().connection().rollback();
            getSession().setFlushMode(oldMode);
            getSession().disconnect();
        }
    }
    
    public void removeRoles( identity id, Collection role_infos) {
        try {
            FlushMode mode = getSession().getFlushMode();
            getSession().setFlushMode(FlushMode.AUTO);
            for (Iterator j = role_infos.iterator(); j.hasNext() ; ) {
                identity_role_info info  = ( identity_role_info ) j.next();
                //                info.setIdentity_role(null);
                getSession().delete(info);
                //                getSession().evict(info);
            }
            
            getSession().connection().commit();
            
            //            getSession().refresh(id);
            getSession().evict(id);
            getSession().connection().commit();
            getSession().setFlushMode(mode);
            getSession().disconnect();
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        
    }
    
    public identity getIdentityById( Long id) {
       return loadIdentity( getSession(), id);
        
    }
    
    
    identity loadIdentity( Session sess,  Long id) {
         identity iden = null;
         
        try {
            iden = (identity)sess.load(identity.class, id);
            
//            Iterator j = sess.iterate("select i from identity i inner join i.social_identitys si "+
//                " where i.id = ? ", id, Hibernate.LONG);
//            if (j.hasNext()) {
//                iden = (identity) j.next();
//            }
//            
        } catch (Exception e)  {
            e.printStackTrace();
        }
        return iden;
        
    }
}
