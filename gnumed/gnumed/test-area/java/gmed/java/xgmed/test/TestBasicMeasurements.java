/*
 * TestBasicMeasurements.java
 *
 * Created on 13 July 2003, 22:54
 */

package  xgmed.test;
import xgmed.domain.accountability.*;
import java.util.*;
import cirrus.hibernate.*;
import cirrus.hibernate.type.Type;
import xgmed.domain.accountability.*;
import xgmed.domain.planning.*;
import xgmed.domain.planning.resource.*;
import xgmed.domain.common.*;
import xgmed.domain.observation.*;

import junit.framework.*;
/**
 * Testing persistence of Measurements.
 * @author  syan
 */
public class TestBasicMeasurements extends TestBasicObservation {
    static final String SYSBP = getResourceName("systolic_bp");
    static final String DIASBP = getResourceName("diastolic_bp");
     static final String TEMP=getResourceName("temp");
      static final String RR=getResourceName( "resp_rate");
      static final String PR = getResourceName("pulse_rate");
      static final String PEFR =getResourceName( "PEFR");
  //  static final String[] names =new String[] { "bp", "weight", "height", "abdominal circumference", "fundal height", "temp", "pulse rate", "respiratory rate", "peak exp flow rate" };
    /** basic unit names. */
    static final String[] basicUnits = new String[] { "mmHg", "kg", "cm", "celcius", "beats", "breaths", "minute", "second", "mls" };
    /** compound unit phrases. */
    static final String[] compoundUnits = new String[] { "beats/minute", "breaths/minute", "mls/second" };
    
    /** test data for measurement phenomenontypes with units. */
    
    Object[][] testData;
    
    /** initialize the test phenomenon type data for loading */
    void initTestData() throws Exception {
        testData= new Object[][] {
            new Object [] {SYSBP, findUnit("mmHg") },
            new Object [] {DIASBP, findUnit("mmHg") },
            new Object [] {TEMP, findUnit("celcius") },
            new Object [] {RR, findUnit("breaths/minute") },
            new Object [] {PR, findUnit("beats/minute") },
            new Object [] {PEFR, findUnit("mls/second") }
        };
    }
    
    Object[][] getTestData() {
        return testData;
    }
    
    /** get a list of phenomenon types that match
     * a description.
     */
    List getTypeList(String name) throws Exception {
        Session s = getSessions().openSession();
        List l = s.find("from p in class xgmed.domain.observation.PhenomenonType where p.description=?", name, Hibernate.STRING);
        s.close();
        return l;
    }
    
    /** get a particular phenomenon type by description. */
    PhenomenonType findType(String name) throws Exception {
        return (PhenomenonType) getTypeList(name).get(0);
    }
    
    /** find a basic unit by name, if none found, create it and
     * return it.
     * @param name
     * @throws Exception
     * @return the unit with the label.
     */
    AtomicUnit createOrFindBasicUnit(String name) throws Exception {
        Session s = getSessions().openSession();
        List l = s.find("from u in class xgmed.domain.common.AtomicUnit where u.label=?", name, Hibernate.STRING);
        if (l.size() == 0)
            return createAtomicUnit(name);
        return (AtomicUnit) l.get(0);
        
    }
    
    /** create an atomic unit by that name and save it. */
    AtomicUnit createAtomicUnit(String name)throws Exception  {
        Session s = getSessions().openSession();
        AtomicUnit u = new AtomicUnit();
        //        u.setId(null);
        u.setLabel(name);
        s.save( u);
        s.flush();
        s.connection().commit();
        s.close();
        return u;
    }
    
    /** create the basic units  in the list of names. */
    void createBasicUnits( String[] names)  throws Exception {
        for (int i = 0; i < names.length; ++i)
            createOrFindBasicUnit(names[i]);
    }
    
    /** gets the split of the a string using the regex
     * @param name the string to parse.
     * @param delim the delimiter to match
     * @return a list of tokens separated by the delimiter
     * occuring in the parsable string.
     */
    String [] getSplit(String name, String delim) {
        String [] parts = name.split(delim, 2);
        return parts;
    }
    /** the syntax of a compount unit name should be 'a.b.c/d/e/f'
     * @param name the name of the compound unit.
     * @throws Exception
     * @return a compound unit with the name.
     *
     */
    CompoundUnit createCompoundUnit(String name ) throws Exception {
        CompoundUnit cu = new CompoundUnit();
        String[] parts = name.split("/", 2);
        String[] atomics = parts[0].split(".");
        String[] inverses = parts[1].split("/");
        for (int i = 0; i < atomics.length; ++i) {
            AtomicUnit u = createOrFindBasicUnit(atomics[i]);
            cu.addAtomicUnit(u);
        }
        for (int i = 0; i < inverses.length; ++i) {
            AtomicUnit u = createOrFindBasicUnit(inverses[i]);
            cu.addInverseUnit(u);
        }
        return cu;
    }
    
    /** create compound units of each name listed.
     * @param names the names of the compound unit,
     * which are composed of basic unit
     * names.
     * @throws Exception
     */
    void createCompoundUnits( String[] names) throws Exception {
        Session s = getSessions().openSession();
        for (int i = 0; i < names.length; ++i) {
            CompoundUnit cu = null;
            List l = s.find("from x in class xgmed.domain.common.CompoundUnit where x.label=?", names[i], Hibernate.STRING);
            if (l.size() != 0)
                cu = (CompoundUnit) l.get(0);
            else {
                s.flush();
                cu = createCompoundUnit(names[i]);
                cu.setLabel(names[i]);
                s.saveOrUpdate(cu);
                s.flush();
            }
        }
     
        s.connection().commit();
        s.close();
    }
    
    /** find any unit with the name. */
    Unit findUnit( String name) throws Exception {
        Session s = getSessions().openSession();
        List l = s.find("from x in class xgmed.domain.common.Unit where x.label=?", name, Hibernate.STRING);
        s.close(); // when this s.close() was missing, an attempt is made to find the Unit before it is created elsewhere.
        // this close statement seems to make this find session serializable with the creation
        // of the unit in createAtomicUnit and createCompoundUnit.
        return (Unit) l.get(0);
    }
    
    /** find a list of phenomnoen types.
     * @throws Exception
     * @return
     */
    Collection getTypes() throws Exception {
        return null;
    }
    
    /** sets up basic types and the hibernate mappings (hbm.xml ) files.
     * @throws Exception
     */
    public void setUp() throws Exception {
        super.setUp();
        createBasicUnits(basicUnits);
        createCompoundUnits(compoundUnits);
        initTestData();
    }
    /** gets a person with attacked observations.
     * @throws Exception
     * @return person with observations.
     */
    public Person getPatientWithObservation( ) throws Exception {
        Person p = getPersonWithMeasurementObservations(super.getPatientWithObservation());
        p.addPartyType(getPartyType(PATIENT));
       
        return p;
    }
    
    
    Quantity getQuantity(PhenomenonType type, double value) {
         Quantity q = new Quantity();
         //**************************************
            // at this point the Unit object is shared.
            // hibernate 1.2 gives error when updating unit again.
            // try a copy
        q.setUnit(type.getUnit());
        q.setNumber(new Double(value));
        return q;
    }
    
    Measurement getMeasurement( String type, double qty) throws Exception  {
         Measurement m = new Measurement();
        PhenomenonType t = findType(type);
        m.setQuantity(getQuantity(t , qty));
        m.setPhenomenonType(t);
        return m;
    }
    
    public Person getPersonWithMeasurementObservations(Person p) throws Exception {
        return addMeasurementObservations(p);
    }
    
    public Person addMeasurementObservations(Person p) throws Exception {
        p.addObservation(getMeasurement(SYSBP, 100.0 + getRandom().nextDouble() % 40.0 ));
        p.addObservation(getMeasurement(DIASBP,60.0 + getRandom().nextDouble() % 30.0 ));
        p.addObservation(getMeasurement(TEMP, 36.0 + getRandom().nextDouble() % 2.0 ));
        p.addObservation(getMeasurement(RR, 10 + getRandom().nextDouble() % 10.0));
         p.addObservation(getMeasurement(PEFR, 400 + getRandom().nextDouble() % 400.0));
         p.addObservation(getMeasurement(PR, 40 + getRandom().nextDouble() % 70.0));
        return p;
    }
    
    
    /** test the regex String.split() method for
     * parsing compound unit strings.
     */
    public void testSplit() {
        for (int i = 0; i < compoundUnits.length; ++i) {
            String[] split = getSplit(compoundUnits[i], "/");
            for (int j = 0; j < split.length; ++j) {
                System.out.print("part=" + split[j] + " ");
            }
            
            System.out.println("Split = "  + split);
            // assertTrue( getSplit(compoundUnits[i], "/").length == 2);
        }
        
    }
    
    /** check the basic units are persistable. */
    public void testBasicUnits() throws Exception {
        
        Session s = getSessions().openSession();
        List l = s.find("from x in class xgmed.domain.common.Unit");
        for (int i = 0; i < l.size(); ++i) {
            Unit u = (Unit) l.get(i);
            System.out.println("Found unit + " + u + " with label = " + u.getLabel());
        }
        s.flush();
        s.close();
        
    }
    
    /** find a list of phenomenon types that match the string in description. */
    List findPhenomenonType(String name) throws Exception {
        Session s = getSessions().openSession();
        List l= s.find("from x in class xgmed.domain.observation.PhenomenonType where x.description=?", name, Hibernate.STRING);
        s.close();
        return l;
    }
    
    /** create a measurement phenomenon type of the
     * given unit.
     */
    PhenomenonType createMeasurementPhenomenonType(String name, Unit unit) throws Exception {
        List l = findPhenomenonType(name);
        if (l.size() > 0)
            return (PhenomenonType) l.get(0);
        PhenomenonType type = new PhenomenonType();
        type.setDescription(name);
        type.setUnit(unit);
        Session s = getSessions().openSession();
        Transaction t = s.beginTransaction();
        s.save(type);
        t.commit();
        s.close();
        return type;
    }
    
    /** check the measurement phenomenon types are persistable. */
    public void testMeasurementPhenomenonType() throws Exception {
        //        Object[][] testData = new Object[][] {
        //            new Object [] {"blood pressure", findUnit("mmHg") },
        //            new Object [] {"temperature", findUnit("celcius") },
        //            new Object [] { "respiratory rate", findUnit("breaths/minute") },
        //            new Object [] { "heart rate", findUnit("beats/minute") },
        //            new Object [] { "peak expiratory flow rate", findUnit("mls/second") }
        //        };
        
        List l =  createListOfTestPhenomenonTypes();
        showCreatedPhenomenonTypes(  l);
        assertCreatedPhenomenonTypes();
    }
    
    /** using the test data "testData" , create some measurement phenomenon types with a
     * reference unit.
     */    
    List createListOfTestPhenomenonTypes() throws Exception {
        List l = new ArrayList();
        for (int i = 0; i < getTestData().length; ++i) {
            String name = (String) getTestData()[i][0];
            Unit unit = (Unit) getTestData()[i][1];
            PhenomenonType type = createMeasurementPhenomenonType(name, unit);
            l.add(type);
        }
        return l;
    }
    
    /** show the created list of phenomenon types. */    
    void showCreatedPhenomenonTypes( List l) {
        for (int j = 0; j < l.size(); ++j) {
            PhenomenonType type = (PhenomenonType) l.get(j);
            System.out.println(" type created " + type + " with unit " + type.getUnit());
            System.out.println("descriptions : " + type.getDescription() + " - " +type.getUnit().getLabel());
        }
    }
    
    
    /** assert the test data phenomenon type descriptions are locatable in the database. */
    void assertCreatedPhenomenonTypes() throws Exception {
        
        Session s = getSessions().openSession();
        for ( int k = 0; k < getTestData().length ; ++k) {
            String name = (String) getTestData()[k][0];
            Unit unit = (Unit) getTestData()[k][1];
            
            List l2 = s.find("select p from p in class xgmed.domain.observation.PhenomenonType where p.description= ? and p.unit.label = ?",
            new Object[] { name, unit.getLabel() }, new Type[] { Hibernate.STRING, Hibernate.STRING } );
            
            PhenomenonType t = assertMatchingPhenomenonType(l2, name, unit);
            
            System.out.println("Found matching phenomenonType "  + t.getDescription() + " with unit " + t.getUnit().getLabel() );
        }
        s.close();
    }
    
    /** assert that there is pne phenomenon type with matching name and unit. */    
    private PhenomenonType assertMatchingPhenomenonType(List l2,  String name, Unit unit) {
        assertTrue("There is no PhenomenonType " + name + " with unit " + unit.getLabel(), l2.size() > 0);
        
        PhenomenonType t = (PhenomenonType) l2.get(0);
        
        assertTrue("phenomenonType " + t.getDescription() + " does not match " + name + " or unit " + t.getUnit().getLabel() + " does not match " + unit.getLabel(),
        t.getDescription().equals(name) && unit.getLabel().equals( t.getUnit().getLabel()) );
        
        return t;
    }
    
    /** Creates a new instance of TestBasicMeasurements */
    public TestBasicMeasurements() {
        testSplit();
    }
    
    /** get a test suite. */
    public static TestSuite suite() {
        
        TestSuite suite= new TestSuite();
        suite.addTestSuite(TestBasicMeasurements.class);
        return suite;
    }
    
    /** run test suite
     * @param args
     */
    public static void main(String args[]) {
        new TestBasicMeasurements();
        junit.textui.TestRunner.run(suite());
    }
}
