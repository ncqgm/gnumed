/*
 * TestScript.java
 *
 * Created on 31 July 2003, 06:18
 */

package gnmed.test;


import org.gnumed.gmIdentity.*;
import org.gnumed.gmGIS.*;
import org.gnumed.gmClinical.*;
import org.drugref.disease_code;
import org.drugref.product;
import org.drugref.atc;
import org.drugref.package_size;

import net.sf.hibernate.*;
import junit.framework.*;
import java.util.*;
import java.util.logging.*;

/**
 *
 * @author  sjtan
 */
public class TestScript extends TestCase {
    static int N_TEST_PRODUCTS = 100;
    static TestClinHealthIssue testIssues  = new TestClinHealthIssue();
    static TestGmGIS testGIS = new TestGmGIS();
    Random r = new Random();
    List idProducts;
    /** Creates a new instance of TestScript */
    public TestScript() {
        try {
            
        initDrugs();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    void initDrugs() throws Exception {
        initProductIdList();
        
    }
    
    void initProductIdList() throws Exception {
        Session s = HibernateInit.openSession();
        String query = "select p.id from  org.drugref.product p";
        idProducts = s.find(query);
        s.close();
    }
    
    product getRandomProduct(Session s) throws Exception {
        int j = r.nextInt(idProducts.size());
            Integer id = (Integer) idProducts.get(j);
            product p = (product) s.iterate("from p in class org.drugref.product where p.id = ? ", id, Hibernate.INTEGER).next();
            
            return p;
    }
    
    public void testGetProducts() throws Exception {
        Session s = HibernateInit.openSession();
        for( int i = 0; i < N_TEST_PRODUCTS; ++i) {
            product p = getRandomProduct(s);
            System.out.print("Found product " + p.getId() );
            if (p.getComment() != null)
                 System.out.print("Comment is " + p.getComment());
            if (p.getDrug_routes() != null)
                System.out.print(" , route is " + p.getDrug_routes().getDescription());
            if (p.getDrug_units() != null)
            System.out.print("; unit is "+ p.getDrug_units().getUnit());
            if (p.getDrug_formulations() != null)
            System.out.print("; formulation is "+p.getDrug_formulations().getDescription()+" : ");
//            System.out.println("Associated drug element = " + p.getDrug_element().getCategory() + " : " + p.getDrug_element().getDescription());
            for (Iterator k = p.getDrug_element().getAtcs().iterator(); k.hasNext(); ) {
                atc atc = (atc) k.next();
                System.out.print(atc.getText());
                if (k.hasNext())
                    System.out.print(", ");
                else
                    System.out.println();
            }
            for (Iterator k = p.getPackage_sizes().iterator(); k.hasNext();) {
                package_size pz = (package_size) k.next();
                System.out.println("\t size="+pz.getSize());
            }
            
            s.evict(p);
        }
        s.close();
    }
    
    public script_drug createRandomScriptDrug(Session s) throws Exception {
        script_drug sd = new script_drug();
        product p = getRandomProduct(s);
        package_size pz = null;
	if (p.getPackage_sizes().size() > 0) {
         int    n = r.nextInt( (int)p.getPackage_sizes().size() );
            pz =  ( package_size)p.getPackage_sizes().iterator().next();
        }
            
        sd.setPackage_size(pz);
        sd.setDose_amount(new Double( (double)(r.nextInt(4) + 1) /(double)2.0));
        sd.setCurrent(new Boolean(true));
        sd.setDirections("times a specified time period");
        sd.setFrequency(r.nextInt(2) + 1);
        return sd;
    }
    
    public script createTestScript(Collection script_drugs) throws Exception {
        script sc = new script();
        int n = r.nextInt(3)+1;
        for (Iterator i = script_drugs.iterator(); i.hasNext(); ) {
        link_script_drug lsd = new link_script_drug();
        script_drug sd = (script_drug) i.next();
        lsd.setScript_drug(sd);
        lsd.setScript(sc);
        lsd.setRepeats( new Integer(r.nextInt(6) + 1));
        }
        
        return sc;
    }
    
    public void addRandomScriptDrugsToIdentity(identity id , Session s) throws Exception {
        
//        Session s = HibernateInit.getSessions().openSession();
        int n = r.nextInt(8) + 3;
        for (int i = 0; i < n; ++i) {
            script_drug sd = createRandomScriptDrug(s);
            id.addScript_drug(sd);
        }
//        s.close();
    }
    
    public identity createIdentityWithScriptDrugs(Session s) throws Exception {
        identity id = testIssues.createTestIdentityWithHealthIssues( );
        addRandomScriptDrugsToIdentity(id, s);
        return id;
    }
    
    public void testCreateIdentityWithScriptDrugs( ) throws Exception {
        int n = r.nextInt(5)+3;
        List idList = new ArrayList();
        Session s = HibernateInit.openSession();
        for (int i = 0 ; i < n; ++i) {
            identity id = createIdentityWithScriptDrugs(s);
           
            s.save(id);
            s.flush();
            s.connection().commit();
            idList.add( id.getId());
        }
        
        s.close();
        
        Session s2 = HibernateInit.openSession();
        List idenList = new ArrayList();
        for (int j = 0; j < idList.size(); ++j) {
            Integer id = (Integer) idList.get(j);
            identity iden = (identity) s2.load(identity.class, id);
            idenList.add(iden);
        }
        
        for (int k = 0; k < idenList.size() ; ++k) {
            identity id2 = (identity) idenList.get(k);
            System.out.println("\n\n************** RECOVERED **************\n******************\n**********\n");
            DomainPrinter.getInstance().printIdentity(System.out, id2);
        }
        s2.close();
    }
        
        
     
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws Exception {
        HibernateInit.initAll();
        TestSuite suite = new TestSuite();
        suite.addTestSuite(TestScript.class);
        junit.textui.TestRunner.run(suite);
        
    }
}
