/*
 * TestClinEncounter.java
 *
 * Created on 27 July 2003, 12:00
 */

package gnmed.test;


import org.gnumed.gmIdentity.*;
import org.gnumed.gmGIS.*;
import org.gnumed.gmClinical.*;
import org.drugref.disease_code;


import net.sf.hibernate.*;
import junit.framework.*;
import java.util.*;
import java.util.logging.*;

/**
 *
 * @author  sjtan
 */
public class TestClinEncounter extends TestCase {
    static TestClinHealthIssue testIssues  = new TestClinHealthIssue();
    static TestGmGIS testGIS = new TestGmGIS();
    Random r = new Random();
    static interface ClinScenario  {
        String getDescription();
        String getHistory();
        String getExamination();
        String getInvestigation();
        String getTreatment();
        
    }
    
    static class SimpleStringArrayClinScenario implements ClinScenario{
        
        public SimpleStringArrayClinScenario() {
            init();
        }
        
        public void  init() {
            
        }
        /** Holds value of property text. */
        private String[] text;
        
        public String getDescription() {
            return text[0];
        }
        
        public String getHistory() {
            return text[1];
        }
        
        public String getExamination() {
            return text[2];
        }
        
        
        
        public String getInvestigation() {
            return text[3];
        }
        
        public String getTreatment() {
            return text[4];
        }
        
        /** Getter for property text.
         * @return Value of property text.
         *
         */
        public String[] getText() {
            return this.text;
        }
        
        /** Setter for property text.
         * @param text New value of property text.
         *
         */
        public void setText(String[] text) {
            this.text = text;
        }
        
    }
    ClinScenario[] scenarios =
    new TestClinEncounter.SimpleStringArrayClinScenario[] {
        new TestClinEncounter.SimpleStringArrayClinScenario() {
            public void init() {
                setText(new String[] {  "wound","cut hand at work","laceration over dorsum finger, neurovasc intact, no deep structures seen", "xray" ,"ADT given, 1%lignocaine plain, infiltr, 4/0 nylon interrupted" }
                );
            }
        },
        new TestClinEncounter.SimpleStringArrayClinScenario() {
            public void init() {
                setText(new String[] {
                    "cough", "cough, runny nose, fever, ", "chest coarse rhonchi bilateral,no crackles T 37.8", "none","symptomatic; med cert 2/7" }
                
                );
            }
        },
        new TestClinEncounter.SimpleStringArrayClinScenario() {
            public void init() {
                setText(new String[] {  "low back pain", "got this AM, with it, working hard yesterday",
                "no spinous process tender, tender left side > right, SLR nad", "none", "avoid heaving lifting; paracetamol; ibuprofen ;"        }
                );
            }
        }
    };
    
    /** Creates a new instance of TestClinEncounter */
    public TestClinEncounter() {
    }
    
    public clin_encounter createClinEncounter(String description, identity provider, address location) throws Exception {
        clin_encounter encounter = new clin_encounter();
        encounter.setLocation(location);
        encounter.setProvider(provider);
        encounter.setDescription( description);
        return encounter;
    }
    
    public clin_encounter addScenarioTo(clin_encounter encounter, TestClinEncounter.ClinScenario scenario) throws Exception {
        clin_history h = new clin_history();
        h.setNarrative(scenario.getHistory());
        
        clin_physical p = new clin_physical();
        p.setNarrative(scenario.getExamination());
        
        clin_note n = new clin_note();
        StringBuffer sb = new StringBuffer();
        sb.append("Ix : ");
        sb.append(scenario.getInvestigation());
        sb.append("\n");
        sb.append(scenario.getTreatment());
        n.setNarrative(sb.toString());
        
        encounter.addClin_root_item(h);
        encounter.addClin_root_item(p);
        encounter.addClin_root_item(n);
        
        return encounter;
        
    }
    
    identity createTestProvider() throws Exception {
        identity id = TestGmIdentity.createTestIdentity();
        Names n = (Names) id.getNamess().iterator().next();
        n.setFirstnames("Dr."+n.getFirstnames());
        return id;
    }
    
    clin_encounter createEncounterWithRandomScenario() throws Exception {
        TestClinEncounter.ClinScenario scene =  scenarios[r.nextInt(scenarios.length)];
        clin_encounter encounter = createClinEncounter(scene.getDescription(),  createTestProvider(),  testGIS.createRandomAddress());
        encounter = addScenarioTo(encounter, scene);
        return encounter;
    }
    
    
    identity createTestIdentityWithScenarios() throws Exception {
        int n = r.nextInt(10) + 1;
        return createTestIdentityWithScenarios(n);
    }
    
    identity createTestIdentityWithScenarios(int n) throws Exception {
        identity id = testIssues.createTestIdentityWithHealthIssues();
        for (int i = 0; i < n; ++i)
            id.addClin_encounter(createEncounterWithRandomScenario());
        return id;
    }
    
    public List createListOfRandomIdentitiesWithClinEncounters() throws Exception {
        List l = new ArrayList();
        int n = r.nextInt(10) + 10;
        
        for (int i = 0; i < n; ++i) {
            identity id = createTestIdentityWithScenarios();
            l.add(id);
        }
        return l;
    }
    public void testCreateIdentityWithRandomClinEncounter() throws Exception {
        List l = createListOfRandomIdentitiesWithClinEncounters();
        printIdentites(l);
    }
    
    void printIdentites( List l) {
//          clin_encounter dummy = new clin_encounter();
        for (int i = 0; i < l.size(); ++i) {
            identity id = (identity) l.get(i);
//            id.addClin_encounter(dummy);
//            id.removeClin_encounter(dummy);
            System.out.println("AFTER STRESSING COLLECTION ADD");
            DomainPrinter.getInstance().printIdentity(System.out, id);
        }
    }
    
    int countIdentityWithEncounters() throws Exception {
        Session sess0 = HibernateInit.getSessions().openSession();
        java.sql.Connection c = sess0.connection();
        java.sql.Statement s = c.createStatement();
        
        java.sql.ResultSet rs = s.executeQuery("select count(distinct(identity)) from  clin_encounter");
        int count = 0;
        if (rs.next())
            count =  rs.getInt(1);
        c.rollback();
        
        sess0.close();
        return count;
        //
        //          int precount = ((Integer)sess0.iterate("select count(distinct(c.identity)) from org.gnumed.gmClinical.clin_encounter c" ).next()).intValue();
        //         sess0.close();
        //        return precount;
    }
    
    
    public void saveIdentityWithEncounterProviders( Session sess, identity id) throws Exception {
            for (Iterator j =id.getClin_encounters().iterator() ; j.hasNext(); ) {
                clin_encounter e = (clin_encounter) j.next();
                sess.save( e.getProvider());
                sess.save( e.getLocation());
                sess.flush();
                sess.connection().commit();
            }
            sess.save(id);
            sess.flush();
            sess.connection().commit();
            sess.evict(sess);
    }
    
    public void atestStoreRandomIdentityWithClinEncounter() throws Exception {
        //        Session sess0 = HibernateInit.openSession();
        System.out.println("PRECOUNTING identities with encounters");
        //        int precount = ((Integer)sess0.iterate("select count (i) from   org.gnumed.gmIdentity.identity  i  where size(i.clin_encounters) > 0").next() ).intValue();
        int precount = countIdentityWithEncounters();
        System.out.println("Precount = " + precount);
        
        
        List l = createListOfRandomIdentitiesWithClinEncounters();
        
        Session sess = HibernateInit.openSession();
        Logger.global.info("ABOUT TO SAVE " + Integer.toString((int) l.size()));
      for (int i = 0 ; i < l.size() ; ++i) {
            saveIdentityWithEncounterProviders(sess, (identity) l.get(i));
            System.out.println("Created THIS:");
            DomainPrinter.getInstance().printIdentity(System.out, (identity) l.get(i));
        }
        
        sess.close();
        
        
        System.out.println("Fetching postcount");
        //       int postcount = ((Integer)sess2.iterate("select count (i) from   org.gnumed.gmIdentity.identity  i  where size(i.clin_encounters) > 0").next() ).intValue();
        int postcount = countIdentityWithEncounters();
        System.out.println("postcount = " + postcount);
        assertTrue( "Not at least " + Integer.toString(l.size()) + "identities with encounters found: only found "
        + postcount  , postcount >= l.size() + precount );
        System.out.println( "=================================================================================");
        System.out.println( "=================================================================================");
        System.out.println("                                         RETRIEVED IDENTITIES                        ");
        
        System.out.println( "=================================================================================");
        
        printIdentites(l);
        
        
        
    }
    
    
    public void testStressIdentities() throws Exception {
        
        int nEncounter = TestProperties.properties.getIntProperty("stress.encounters.per.identity");
        
        
        int notifyEveryN = TestProperties.properties.getIntProperty("notify.id.at.interval");
        List sampleIds = new ArrayList();
        int nId = TestProperties.properties.getIntProperty("stress.identity.count");
        Logger.global.info("nId = " + Integer.toString(nId) + "nEncounter= " + Integer.toString(nEncounter));
        
        
        
             Session s = HibernateInit.openSession();
           
        for (int i = 0; i <  nId; ++i) {
            identity id = createTestIdentityWithScenarios(nEncounter);
            
            System.out.println("ABOUT TO SAVE");
       
          saveIdentityWithEncounterProviders(s,id);
           s.flush();
            s.connection().commit();
//            for( Iterator j = id.getClin_encounters().iterator(); j.hasNext(); ) {
//                s.update(j.next());
//            }     
//            s.flush();
//            s.connection().commit();
//       
            sampleIds.add(id.getId());
            if (i % notifyEveryN == 0)
                System.out.println("Created "+ i + " identites with " + nEncounter + " each.");
        }
        s.close();
        System.out.println("Saved " + nId + " identities");
        Date d1 = new Date();
        System.out.println("RETRIEVING SAMPLE OF " + sampleIds.size() +" from recently stored identities.");
        List found = new ArrayList();
        Session sess = HibernateInit.getSessions().openSession();
        for (int i = 0; i < sampleIds.size(); ++i) {
            identity id = (identity)sess.load(identity.class, (java.io.Serializable) sampleIds.get(i) );
            id.getClin_encounters().addAll(sess.find("select e from org.gnumed.gmClinical.clin_encounter  e "
                                    +"  where  e.identity.id= ?", id.getId(), Hibernate.INTEGER) );
            sess.flush();
            found.add(id);
        }
        Date d2 = new Date();
        printIdentites(found);
        sess.close();
        
        System.out.println("Time to retrieve " + sampleIds.size() + " identites = " + (d2.getTime() - d1.getTime()));
        
    }
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws Exception {
        HibernateInit.initAll();
        TestSuite suite = new TestSuite();
        suite.addTestSuite(TestClinEncounter.class);
        junit.textui.TestRunner.run(suite);
        
    }
}
