/*
 * TestScriptDrugManager.java
 *
 * Created on 4 August 2003, 10:17
 */

package quickmed.usecases.test;

import org.gnumed.gmIdentity.*;
import org.gnumed.gmGIS.*;
import org.gnumed.gmClinical.*;
import org.drugref.disease_code;
import org.drugref.product;
import org.drugref.atc;
import org.drugref.package_size;
import gnmed.test.*;

import net.sf.hibernate.*;
import net.sf.hibernate.type.*;
import junit.framework.*;
import java.util.*;
import java.util.logging.*;
/**
 *
 * @author  sjtan
 */
public class TestScriptDrugManager {
    
    
    private  static TestScriptDrugManager manager;
    
    
    static {
        manager = new TestScriptDrugManager();
    };
    
    public static TestScriptDrugManager instance() {
        return manager;
    }
    /** Creates a new instance of TestScriptDrugManager */
    protected  TestScriptDrugManager() {
        try {
            HibernateInit.initAll();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    
    /**
     *  finds script_drug objects from an identity that matches a product
     *
     */
    public List findScriptDrug( identity id, product p) throws Exception {
        
        Session sess =  getSession();
        List l = sess.find("select sd from script_drug sd inner join sd.identity i "+
        " where sd.product.id = ? and i.id = ?", new Object[] { p.getId(), id.getId() } ,
        new Type[] { Hibernate.INTEGER, Hibernate.INTEGER }      );
        getSession().disconnect();
        return l;
    }
    
    public void removeScriptDrug( identity id, script_drug sd) {
        id.removeScript_drug(sd);
    }
    
    public  link_script_drug createOrUpdateScriptDrug( identity id, package_size packageSize, Double qty,
    String directions, Integer repeats, script script ) throws Exception  {
        //try to update.
        // ************   Need to deal with multiple duplicate products as well.
        
        script_drug sd = null;
        
        sd =  updateIdentityScriptDrug( id, packageSize , qty,directions,repeats, script);
        
        if (sd == null)
            sd =  createIdentityScriptDrug(id, packageSize , qty,directions,repeats, script);
        link_script_drug lsd = new link_script_drug();
        lsd.setScript(script);
        lsd.setRepeats(repeats);
        lsd.setScript_drug(sd);
        try {
            Logger.global.info("updated/created lsd = " + lsd);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return lsd;
    }
    
    
    /** given a specific package_size object, a qty, instructions and repeats
     * create a script_drug object and add it to the given identity.
     */
    public script_drug createIdentityScriptDrug(identity id, package_size p, Double qty,
    String instructions, Integer repeats, script script) throws Exception {
        script_drug sd = new script_drug();
        sd.setDirections(instructions);
        sd.setQty(qty);
        sd.setPackage_size(p);
        id.addScript_drug(sd);
        
        //        use this later, otherwise may cause transient object error
        //        link_script_drug lsd = new link_script_drug();
        //        lsd.setScript_drug(sd);
        //        lsd.setRepeats(repeats);
        //        lsd.setScript(script);
        return sd;
    }
    
    public script_drug updateIdentityScriptDrug( identity id, package_size pz, Double qty,
    String instructions, Integer repeats, script script ) throws Exception {
        script_drug sd =id.findDrugScriptWithProduct(pz.getProduct(), qty);
        if (sd != null) {
            sd.setQty(qty);
            sd.setDirections(instructions);
            //                sd.addLink_script_drug(lsd); //  CHECK AND FIX LATER
            
        }
        return sd;
    }
    
    /** finds product objects by their generic drug name
     */
    public List findByDrugName( String name) throws Exception {
        List l = null;
        Session s = null;
        try {
            s = getSession();
            l = s.find("select p from product p inner join p.drug_element.generic_name n"
            + " where n.name like ? ",  name + "%" ,   Hibernate.STRING  );
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            try {
                getSession().disconnect();
            } catch (Exception e2) {
                e2.printStackTrace();
            }
        }
        return l;
    }
    
    /**
     *find package_size objects by their drug name
     */
    public List findPackagedProductByDrugName( String name) throws Exception {
        Session s = getSession();
        List l = s.find("select p from package_size p inner join p.product.drug_element.generic_name n"
        + " where n.name like ? ",  name + "%" ,   Hibernate.STRING  );
        
        getSession().disconnect();
        return l;
    }
    
    public List doQuery( String query, String var, boolean closeSession) throws Exception {
        return doQuery(query, var, closeSession, true);
    }
    
    public List doQuery( String query, String var, boolean closeSession, boolean newTransaction) throws Exception {
        Session s = getSession();
        if (newTransaction ) try {
            s.connection().commit();
        } catch (Exception e) {
            
            s.connection().rollback();
            
        }
        List l = s.find(query, var, Hibernate.STRING);
        if (closeSession)
            getSession().disconnect();
        return l;
    }
    public static void  main( String[] args) throws Exception {
        
        
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
