/*
 * AbstractTestCase.java
 *
 * Created on 04 July 2003, 19:53
 */


package  xgmed.test;
import xgmed.helper.*;
import cirrus.hibernate.*;
import cirrus.hibernate.type.Type;
import cirrus.hibernate.tools.SchemaExport;
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

import junit.framework.*;
import java.util.*;
/** base cllass for tests
 * @author sjtan
 */

public class AbstractTestCase extends TestCase {
    /** the sessionFactory to generate sessions. */    
    static SessionFactory sessions;
    
    //private static Configuration config;
    /** the data store for hibernate setup. */    
    static Datastore ds;
    //    private static Configuration ds;
    /** a shared session. */    
    Session s;
    
    /** a random generator to generate names and
     * simulate data.
     */    
    Random r = new Random();
    
    /** */    
    int sampleSpace = 100000;
    
    private   static boolean hasSetup = false;
    /** a patient PartyType. */    
    static PartyType patientType;
    /** a doctor PartyType */    
    static PartyType doctorType ;
    /** a map of party types, ( just in case, handcode
     * some simplistic caching).
     */    
    static Map partyTypes;
    
    /** a name for patient role */    
    public  static String PATIENT = "patient";
    /** a name for doctor role */    
    public   static String DOCTOR = "doctor";
    
    static {
        
        try {
            ds = Hibernate.createDatastore();
            //        ds = new Configuration();
            configureDatastore(ds);
            
            // new SchemaExport(ds).drop(true, true) ;
            boolean exportScript = true;
            System.out.println("property schema.export = "+ System.getProperty("schema.export",""));
            if (System.getProperty("schema.export", "").equals("off") )
                exportScript=false;
            new SchemaExport(ds).create(exportScript, exportScript ) ;
            sessions = ds.buildSessionFactory();
        } catch (Exception e) {
            e.printStackTrace();
        }
        // patient = ResourceBundle.getBundle("concepts").getString(PATIENT);
        partyTypes = new HashMap();
        patientType =  createPartyType(  PATIENT) ;
        doctorType = createPartyType(  DOCTOR);
        partyTypes.put(PATIENT, patientType);
        partyTypes.put(DOCTOR, doctorType);
    }
    
    
    public Random getRandom() {
        return r;
    }
    
    /** configures and returns the datastore (hibernate 1.2)
     * @param ds the datastore
     * @throws Exception
     */
    public static void configureDatastore(
    //    Configuration
    //    /*
    Datastore
    //     */
    ds) throws Exception  {
        ds. storeClass(Telephone.class).
        storeClass(Address.class).
        storeClass(Party.class).  // now (NOT) in Asset.hbm.xml
        storeClass(PartyType.class).
        storeClass(AccountabilityType.class).
        storeClass(Accountability.class).
        storeClass(Action.class).
        storeClass(Suspension.class).
        storeClass(TimeRecord.class).
        storeClass(Quantity.class).
        storeClass(Unit.class).
        storeClass(ConversionRatio.class).
        storeClass(ObservationConcept.class).
        //        the Observation will compile as a subclass using the earlier xdoclet.
        //        storeClass(Observation.class).
        storeClass(ObservationProtocol.class).
        storeClass(PhenomenonType.class).
        storeClass(AssociatedObservationRole.class).
        storeClass(AssociativeFunction.class).
        storeClass(Location.class).
        storeClass(Coding.class).
        storeClass(CodeScheme.class).
        storeClass(AssuranceLevel.class).
        storeClass(Occurence.class).
        storeClass(ResourceAllocation.class).
        storeClass(ResourceType.class).
        storeClass(Holding.class).
        storeClass(Asset.class)
        ;
        
        //        ds.configure("hibernate-mapping-2.0.dtd");
        //        ds.addClass(Telephone.class).addClass(Address.class).addClass(Party.class).
        //        addClass(PartyType.class).addClass(AccountabilityType.class).addClass(Accountability.class);
    }
    
    /** true if schema exported in this process
     * @throws Exception
     */
    
    public boolean hasSetup() {
        return hasSetup;
    }
    
    /** set schema exported status */    
    public void setHasSetup( boolean v) {
        hasSetup = v;
    }
    
    /** sets up any exported databases */    
    public void setUp() throws Exception {
        if (hasSetup() ) {
            sessions = ds.buildSessionFactory();
            return;
        }
        
            /*Hibernate2
                config = new Configuration().
                                addClass(Telephone.class).
                                addClass(Address.class).
                                addClass(Party.class);
             */
        
        setHasSetup(true);
    }
    
    /** tears down , nothing yet. */    
    public void tearDown()  {
        try {
            
            if ( s!= null && s.isConnected()) {
                s.connection().rollback();
                //s.connection().close();
            }
            // this is unnecessary , and wont stop deadlock
            // new SchemaExport(ds).drop(true, true) ;
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        
    }
    
    /** the factory that produces new hibernate sessions
     * @return
     */
    public static SessionFactory getSessions() {
        return sessions;
    }
    /** saves a person ,
     * @param p
     * @param s
     * @throws Exception
     * @deprecated using visitor pattern on domain classes
     */
    public static void savePerson(Person p, Session s) throws Exception {
        Transaction trans = null;
        try {
            trans =s.beginTransaction();
            
            s.saveOrUpdate(p.getAddress());
            Iterator i = p.getTelephones().iterator();
            while (i.hasNext()) {
                s.save(i.next());
            }
            //s.flush();
            s.saveOrUpdate(p);
            s.flush();
            trans.commit();
        } catch (Exception e) {
            trans.rollback();
            throw e;
            
        }
        finally {
            //  trans.commit();
            trans = null;
        }
    }
    
    
    /** creates a person with name, birthdate
     * @throws Exception
     * @return
     */
    public static Person createOnePerson() throws Exception {
        return NameProducer.createRandomPerson();
//        Session s = getSessions().openSession();
//        
//        Person p = null;
//        try {
//            
//            p = NameProducer.createRandomPerson();
//            savePerson(p, s);
//            
//            
//        } catch (Exception e) {
//            e.printStackTrace();
//            p = new Person();
//        }
//        finally {
//            s.flush();
//            s.close();
//        }
        
 //       return p;
    }
    
    /** gets the list of hibernated persons.
     * @throws Exception
     * @return a list containing person objects.
     */
    public List  getAllPersons() throws Exception  {
        if (s == null) {
            SessionFactory f = ds.buildSessionFactory();
            s = f.openSession();
            
        }
        //s.setFlushMode(FlushMode.AUTO);
        List l = s.find("from p in class xgmed.domain.accountability.Person where p.firstNames like '%'");
        return l;
    }
    
    /** gets all persons and prints them
     */
    public void printAnyPersons()throws Exception  {
        Collection c  = getAllPersons();
//        assertTrue( c.size() > 0);
        printPersons(c);
        
        //  s.flush();
        s.connection().close();
        s.close();
        
    }
    
    
    /**
     * @param c
     * @throws Exception
     */
    public void printPersons(Collection c) throws Exception {
        Person p2 = null;
        Iterator j = c.iterator();
        PrintContentVisitor v = new PrintContentVisitor();
        for (int  i =  1; j.hasNext() ; ++i ) {
            p2 = (Person) j.next();
            System.out.print("LISTED Person #"+i);
            p2.accept(v);
        }
    }
    
    
    /**
     * @param p2
     * @throws Exception
     */
    public static void printPerson(Person p2) throws Exception {
        System.out.println(" p2 = " + p2 + " details :name =  " + p2.getFirstNames() + " " + p2.getLastNames());
        System.out.println(" birthdate: " + p2.getBirthdate());
        printPartyTypes(p2.getPartyTypes());
        printAddress(p2.getAddress());
        printTelephones(p2.getTelephones());
        
    }
    
    /** prints any named party types. */    
    public static void printPartyTypes(Collection types) {
//        if (types == null)
//            return;
        for (Iterator i = types.iterator(); i.hasNext();) {
            printPartyType((PartyType) i.next());
        }
    }
    
    /** prints the given party type */    
    public static void printPartyType(PartyType type) {
        System.out.println("The person has a role of " + type.getDescription());
    }
    
    /** prints the address. */    
    public static void printAddress(Address address) {
        System.out.println(address.getStreet() + " , " + address.getPostcode() );
    }
    /** prints the telephone */    
    public static void printTelephones( Collection telephones) {
        Iterator i = telephones.iterator();
        for ( int j = 1; i.hasNext(); ++j) {
            printTelephone( j, (Telephone)  i.next());
        }
    }
    /**
     * @param count the number label (position in collection)
     * @param t2 the telephone object to print
     */    
    public static void printTelephone(int count, Telephone t2) {
        System.out.println("Telephone #"+count +" =" + t2.getNumber());
    }
    
    /** prints a time record */    
    public static void printTimeRecord( TimeRecord r) throws Exception {
        if (r == null) {
            System.out.println(" the time record is null");
            return;
        }
        if ( r instanceof TimePeriod) {
            TimePeriod p = (TimePeriod) r;
            System.out.print("Starting at " );
            printTimeRecord(p.getStart());
            if (p.getIndefinite().booleanValue())
                System.out.println("Period is indefinite");
        }
        
        if (r instanceof Timepoint) {
            Timepoint p = (Timepoint) r;
            System.out.println("Time=" + p.getTimeValue() );
        }
    }
    
    
    /** print an observation */    
    public static void printObservation( Observation o) throws Exception {
        if (o == null)
            System.out.println("Attempted to print null Observation");
        
        if (o.getClass().isAssignableFrom(Measurement.class))
            System.out.println(o + " is a Measurement");
        if (o instanceof IdentityObservation)  {
            printIdentityObservation( (IdentityObservation) o);
            
        } else
            if (o instanceof CategoryObservation )  {
                System.out.println(o + "is a CategoryObservation");
                CategoryObservation c = (CategoryObservation) o;
                System.out.println( c + " has a concept of " + c.getObservationConcept());
                if (c.getObservationConcept() != null)
                    printObservationConcept(c.getObservationConcept());
            }
        printTimeRecord(o.getApplicableTime());
    }
    
    /** print a IdentityObservation */    
    public static void printIdentityObservation( IdentityObservation io) throws Exception {
        System.out.print(io + " is a identity observation with ");
        if (io.getCoding() != null)  {
            System.out.print(io + " coding of ");
            printCoding(io.getCoding());
        } else
            System.out.println("null coding found.");
    }
    
    /** print a coding */    
    public static void printCoding( xgmed.domain.observation.Coding coding) {
        System.out.print(coding);
        if (coding.getCode() != null)
            System.out.print(" has value of " + coding.getCode());
        if ( coding.getCodeScheme() != null)
            System.out.print(" with code scheme of description : " + coding.getCodeScheme().getDescription());
        System.out.println();
    }
    
    /** print a observation concept. */    
    public static void printObservationConcept(ObservationConcept concept) {
        System.out.println("The observation concept has description : "+ concept.getDescription());
        if (concept instanceof Phenomenon)
            printPhenomenon( (Phenomenon) concept);
    }
    
    /** print a phenomenon. */    
    public static void printPhenomenon( Phenomenon phenomenon) {
        System.out.println("The concept is a phenomenon of type " + phenomenon.getPhenomenonType());
        if (phenomenon.getPhenomenonType() != null)
            System.out.println("The phenomenon type is " + phenomenon.getPhenomenonType().getDescription() );
    }
    
    /** add more telephone numbers to the person. */    
    public  Person addMoreNumbers(Person p) {
        for (int i = 0; i < r.nextInt(6); ++i) {
            Telephone t = new Telephone();
            t.setNumber( new Long(Math.abs( r.nextInt(1000000))) .toString());
            p.addTelephone(t);
        }
        return p;
    }
    
    /** create a person with multiple telephone numbers. */    
    public Person createPersonWithMultiTelephones() throws Exception {
        Person p = createOnePerson();
        p = addMoreNumbers(p);
        return p;
    }
    /**
     * @param description
     * @return
     */
    public static PartyType createPartyType(String description) {
        PartyType type = new PartyType();
        type.setDescription(description);
        return type;
    }
    
    /** get a party type by description. */    
      public   PartyType getPartyType(String type) {
        return (PartyType) partyTypes.get(type);
    }
    
    /**
     * @param description
     * @param commissionerType
     * @param responsibleType
     * @return
     */
    public AccountabilityType createAccountabilityType( String description,  PartyType commissionerType, PartyType responsibleType) {
        AccountabilityType accountType = new AccountabilityType();
        accountType.addCommissioner(commissionerType);
        accountType.addResponsible(responsibleType);
        return accountType;
    }
    
    /**
     * @param accType
     * @param patient
     * @param doctor
     * @return
     */
    public Accountability  createAccountability(AccountabilityType accType,  Party patient, Party doctor) {
        Accountability acc = new Accountability();
        acc.setAccountabilityType(accType);
        acc.setCommissioner(patient);
        acc.setResponsible(doctor);
        return acc;
    }
    
    /** make sure the party type exists (by finding on the description). */    
    public void assertPartyTypesExist(Person p) {
        assertTrue("no party type", p.getPartyTypes().size() > 0);
    }
    
    /** assert the there are telephone numbers for the person object. */    
    public void assertTelephonesExist(Person p) {
        assertTrue("No telephones exist for "   +p.getFirstNames() + " " +p.getLastNames(), 
                    p.getTelephones().size() > 0);
    }
    
    
    /** find a person by lastnames ,firstnames. */    
    Person findPerson(Session s, String lastNames, String firstNames) throws Exception {
        List l =  s.find("from p in class xgmed.domain.accountability.Person where p.lastNames like ? and p.firstNames like ?",
        new Object[] { lastNames, firstNames }, new Type[] { Hibernate.STRING, Hibernate.STRING } );
        return (Person) l.get(0);
    }
    
    /** Creates a new instance of AbstractTestCase */
    public AbstractTestCase() {
    }
    
    /**
     * @return
     */
    public static TestSuite suite() {
        return new TestSuite();
    }
    /** run test suite */
    public static void main(String args[]) {
        
        junit.textui.TestRunner.run(suite());
    }
    
    public static String getResourceName(String name) {
        return ResourceBundle.getBundle("ObservationConcept").getString(name);
    }
}
