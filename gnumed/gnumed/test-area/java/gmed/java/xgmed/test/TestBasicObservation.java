 /*
 * TestPatientRegistration.java
 *
 * Created on 04 July 2003, 19:51
 */

package  xgmed.test;
import cirrus.hibernate.*;
import cirrus.hibernate.type.Type;
import cirrus.hibernate.tools.SchemaExport;
import cirrus.hibernate.type.*;
// hibernate2
//import cirrus.hibernate.cfg.Configuration;
//import net.sf.hibernate.*;
//import net.sf.hibernate.cfg.Configuration;
//import net.sf.hibernate.type.*;
//import net.sf.hibernate.tool.hbm2ddl.SchemaExport;

import xgmed.domain.accountability.*;
import xgmed.domain.planning.*;
import xgmed.domain.planning.resource.*;
import xgmed.domain.common.*;
import xgmed.domain.observation.*;
import xgmed.helper.*;

import junit.framework.*;
import java.util.*;
/**
 *
 * @author  sjtan
 */
public class TestBasicObservation extends AbstractTestCase {
    static CodeScheme medicare;
    static ObservationConcept conceptPublicHealthId , conceptLiving  ;
    static PhenomenonType sex;
    static Phenomenon male, female;
    static {
        medicare = new CodeScheme();
        medicare.setDescription(getResourceName("public_health_scheme"));
        conceptPublicHealthId = new ObservationConcept();
        conceptPublicHealthId.setDescription(getResourceName("public_health_id"));
        conceptLiving = new ObservationConcept();
        conceptLiving.setDescription(getResourceName("living"));
        sex = new PhenomenonType();
        sex.setDescription(getResourceName("sex"));
        male = new Phenomenon();
        female = new Phenomenon();
        male.setDescription(getResourceName("male"));
        female.setDescription(getResourceName("female"));
        male.setPhenomenonType(sex);
        female.setPhenomenonType(sex);
        try {
            Session s = getSessions().openSession();
            Transaction t = s.beginTransaction();
            s.saveOrUpdate(medicare);
            s.saveOrUpdate(conceptLiving);
            s.saveOrUpdate(conceptPublicHealthId);
            s.save(sex);
            s.save(female);
            s.save(male);
            
            
            
            t.commit();
            s.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    };
    
    void persist(Object o) throws Exception {
        Session s = getSessions().openSession();
        Transaction t = s.beginTransaction();
        s.save(o);
        s.flush();
        t.commit();
        s.close();
        System.out.println(o + " was persisted");
    }
    
    public Observation putTimeStamp(Observation o, TimeRecord recording, TimeRecord applicable) throws Exception {
        persist(recording);
        persist(applicable);
        o.setRecordTime(recording);
        o.setApplicableTime(applicable);
        return o;
    }
    
    
    
    public IdentityObservation getPublicHealthIdentity( String code) throws Exception {
        Coding medicareNo = new  Coding();
        medicareNo.setCodeScheme(medicare);
        medicareNo.setCode(code);
        
        IdentityObservation obs = new IdentityObservation();
        
        Timepoint t = new Timepoint();
        t.setTimeValue(new java.util.Date());
        obs.setRecordTime(t);
        obs.setApplicableTime(t);
        obs.setObservationConcept(conceptPublicHealthId);
        obs.setCoding(medicareNo);
        return obs;
    }
    
    /** gets a new  Living  CategoryObservation, with the applicability
     * set to indefinite, with a start time of birth date.
     */
    public CategoryObservation getLiving( Date birth) throws Exception {
        CategoryObservation obs = new CategoryObservation();
        obs.setObservationConcept(conceptLiving);
        Timepoint t = new Timepoint();
        t.setTimeValue(birth);
        TimePeriod period = new TimePeriod();
        period.setStart(t);
        period.setIndefinite( Boolean.TRUE);
        Timepoint observed = new Timepoint();
        obs.setApplicableTime(period);
        obs.setRecordTime(observed);
        return obs;
    }
    
    /**
     * get a new Category Observation of which Phenomenon , male or female.
     */
    public CategoryObservation getSex( boolean isMale) {
        CategoryObservation obs = new CategoryObservation();
        obs.setObservationConcept( isMale ? male: female);
        return obs;
    }
    
    Person getPersonWithBasicObservations(Person p) throws Exception {
        p.addPartyType(getPartyType(PATIENT));
        p.addObservation(getPublicHealthIdentity("444556 777"));
        p.addObservation(getLiving(p.getBirthdate()));
        p.addObservation(getSex( p.isMale()));
        return p;
    }
    
    public Person getPatientWithObservation() throws Exception {
        Person p = createPersonWithMultiTelephones( );
        return getPersonWithBasicObservations(p);
    }
    
    public void  testPatientRegistration() throws Exception {
        Person p = getPatientWithObservation();
        System.out.println("GETTING BACK PERSON WITHOUT SAVING ");
        printPerson(p);
        PrintContentVisitor visitor = new PrintContentVisitor();
        p.accept(visitor);
        System.out.println("PERSON DISCARDED  ");
    }
    
    
    public static void savePerson(Person p) throws Exception {
        Session s = getSessions().openSession();
        s.save(p);
        s.flush();
        System.out.println("Saved Observations="+p.getObservations().size());
        s.connection().commit();
        s.close();
        //        System.exit(0);
    }
    
   
    
   
    public List findPersonsWithNames( String lastName, String firstName ) throws Exception {
        Session s = getSessions().openSession();
        return s.find( "from p in class xgmed.domain.accountability.Person where p.lastNames like ? and p.firstNames like ?",
        new Object[] { lastName, firstName },
        new Type[] { Hibernate.STRING, Hibernate.STRING } );
        
    }
    
    public void testPersistentPatient() throws Exception {
        Person p = getPatientWithObservation();
        assertTrue("No observations created before saving person p", p.getObservations().size() > 0);
        //        AbstractTestCase.savePerson(p, getSessions().openSession());
        
         savePerson(p);
        
        Date birth = p.getBirthdate();
        System.out.println("ATTEMPTED TO SAVE THIS PERSON:");
        PrintContentVisitor contentVisitor = new PrintContentVisitor();
        printPerson(p);
        System.out.println("THE CONTENT OF " + p + " IS :");
        p.accept(contentVisitor);
        assertPartyTypesExist(p);
        
        List l = findPersonsWithNames(p.getLastNames(), p.getFirstNames() );
        p = null;
        assertTrue( l.size() > 0);
        p = (Person) l.get(0);
        
        System.out.println("GOT BACK THIS PERSON:");
        printPerson(p);
        p.accept(contentVisitor);
        
        System.out.println("All persons are:");
        printAnyPersons();
        assertTrue(p.getBirthdate().getTime() == birth.getTime());
        assertTrue("no observations found after retrieving person", p.getObservations().size() > 0);
        StringBuffer q = new StringBuffer();
        q.append("select o from o in class xgmed.domain.observation.CategoryObservation,");
        //        q.append("gender in class xgmed.domain.observation.Phenomenon,");
        //       q.append("sex in class xgmed.domain.observation.PhenomenonType ,");
        q.append("p in class xgmed.domain.accountability.Person ");
        q.append(" where o.subject = p  and  p.firstNames like ? and p.lastNames like ?");
        //        q.append(" and o.observationConcept = gender");
        //            q.append("and gender.phenomenonType = sex and sex.description =?");
        //
        //
        
        s = getSessions().openSession();
        List obs = s.find(q.toString(),
        new Object[] { p.getFirstNames(), p.getLastNames() 
        //        , "sex"
        },
        new Type[] { Hibernate.STRING, Hibernate.STRING
        //        , Hibernate.STRING
        }
        );
        assertTrue(  "no obs found" , obs.size() > 0 );
        
        StringBuffer q2 = new StringBuffer();
        //        q2.append("from ph in class xgmed.domain.observation.PhenomenonType");
        q2.append("select ph from ph in class xgmed.domain.observation.PhenomenonType where ph.description='sex'");
        
        List phens = s.find(q2.toString());
        
        
        for (int i = 0; i < obs.size(); ++i) {
            printObservation((Observation)obs.get(i));
        }
        //      assertTrue(  "too many observations found" , obs.size() == 1);
        assertTrue( "Obs found but not a CategoryObservation", CategoryObservation.class.isAssignableFrom(obs.get(0).getClass()));
        //        CategoryObservation ob = (CategoryObservation) obs.get(0);
        //        assertTrue( ob.getObservationConcept().getClass().isAssignableFrom(Phenomenon.class));
        //        Phenomenon phen = (Phenomenon) ob.getObservationConcept();
        //        assertTrue( phen.getPhenomenonType().getDescription().equals("sex"));
        assertPartyTypesExist(p);
    }
    
    public void testObservationsAddedToPersistedPerson() throws Exception {
        Session s = getSessions().openSession();
        Person p = createOnePerson();
        s.save(p);
        s.flush();
        s.connection().commit();
 
        s.close();
         List l1 = findPersonsWithNames(p.getLastNames(), p.getFirstNames() );
         assertTrue( "no   person saved", l1.size() > 0);
         assertTrue("more than one person saved", l1.size() == 1);
        Session s2 = getSessions().openSession();
        
        p = getPersonWithBasicObservations(p);
        System.out.println("PERSON BEFORE SAVING");
        printPerson(p);
        s2.update(p);
        s2.flush();
//        p.accept(visitor);
//        visitor.getSession().flush();
       s2.connection().commit();
       s2.close();
       
         List l = findPersonsWithNames(p.getLastNames(), p.getFirstNames() );
        p = null;
        assertTrue( l.size() > 0);
        p = (Person) l.get(0);
        
        System.out.println("GOT BACK THIS PERSON:");
        printPerson(p);
        PrintContentVisitor pvisitor = new PrintContentVisitor();
        p.accept(pvisitor);
        
        
        for ( int i = 1; i < l.size(); ++i) {
            System.out.println("OTHER PERSON WITH NAME:");
            printPerson((Person)l.get(i));
        }
        assertTrue("More than one person with this name",  l.size() < 2);
        assertTrue( "no observations saved", p.getObservations().size() > 0);
    }
    public static TestSuite suite() {
        TestSuite suite= new TestSuite();
        suite.addTestSuite(TestBasicObservation.class);
        return suite;
    }
    /** run test suite */
    public static void main(String args[]) {
        
        junit.textui.TestRunner.run(suite());
    }
    
    
}
