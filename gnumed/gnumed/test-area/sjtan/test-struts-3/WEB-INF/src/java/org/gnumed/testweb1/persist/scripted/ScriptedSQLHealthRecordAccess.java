/*
 * ScriptedSQLHealthRecordAccess.java
 *
 * Created on September 14, 2004, 10:54 PM
 */

package org.gnumed.testweb1.persist.scripted;
import org.gnumed.testweb1.persist.HealthRecordAccess01;
import org.gnumed.testweb1.persist.DataSourceUsing;
import org.gnumed.testweb1.persist.DataObjectFactoryUsing;
import org.gnumed.testweb1.data.*;
import org.gnumed.testweb1.persist.DataSourceException;
import org.gnumed.testweb1.global.Constants ;
import org.gnumed.testweb1.global.Algorithms;
import java.util.*;
import java.sql.*;
import org.apache.commons.logging.*;

/**
 *
 * @author  sjtan
 */
public class ScriptedSQLHealthRecordAccess implements
HealthRecordAccess01, DataSourceUsing, DataObjectFactoryUsing  {
    javax.sql.DataSource dataSource;
    org.gnumed.testweb1.data.DataObjectFactory factory;
    
    // THIS MIGHT NEED TO BE A SEPARATE SERVICE, in order for multi-thread to work.
    //
    private  Map accessedRecords = new HashMap();
    
    /** change the fields for aliasing , if field names change
     */
    
    private org.gnumed.testweb1.persist.ClinicalDataAccess clinicalDataAccess;
    
    private static final String HEALTH_ISSUE_ATTRIBUTES = "hi.id as id, hi.description as description ";
    private static final String CLIN_EPISODE_ATTRIBUTES = "id as id, modified_when as modified_when, description as description";
    private static final String CLIN_ROOT_ITEM_ATTRIBUTES= "pk_item as id, clin_when as clin_when , soap_cat as soap_cat, narrative as narrative";
    private static final String CLIN_NARRATIVE_ATTRIBUTES = CLIN_ROOT_ITEM_ATTRIBUTES + ", is_rfe as is_rfe, is_aoe as is_aoe";
    
    static double WORD_THRESHOLD = 0.7;
    
    static double MATCHED_WORDCOUNT_THRESHHOLD = 0.7;
    
    static long SAME_EPISODE_INTERVAL =  5 * 1000; // 5 seconds
    
    static Log log= LogFactory.getLog(ScriptedSQLHealthRecordAccess.class);
    
    /** Creates a new instance of ScriptedSQLHealthRecordAccess */
    public ScriptedSQLHealthRecordAccess() {
    }
    
    public Map getAccessedRecords() {
        return Collections.synchronizedMap(accessedRecords);
    }
    
    public HealthRecord01 findHealthRecordByIdentityId(long patientId) throws org.gnumed.testweb1.persist.DataSourceException {
       /*
        Map accessedRecords = getAccessedRecords();
        if (accessedRecords.containsKey(new Long(patientId)) ) {
            return (HealthRecord01) accessedRecords.get(new Long(patientId));
        
        }
        
        */
        Connection conn = null;
        try {
            conn = dataSource.getConnection();
            conn.setReadOnly(true);
            
            
            
            ResultSet healthIssuesRS, episodesRS, encountersRS,
            vaccinationsRS, medicationsRS, allergyRS, narrativeRS,
            lab_requestRS, test_resultRS, referralRS, encounterTypeRS;
            
            ensureXLinkIdentityExists(conn, patientId);
            healthIssuesRS = getHealthIssueRS(conn, patientId);
            
            episodesRS = getClinEpisodesRS(conn, getIdsFromResultSet(healthIssuesRS, "id"));
            encountersRS = getClinEncountersRS(conn, patientId);
            long[] encounter_ids  = getIdsFromResultSet(encountersRS, "id");
            
            vaccinationsRS = getVaccinationRS(conn, encounter_ids);
            medicationsRS= getMedicationRS(conn, encounter_ids);
            allergyRS= getAllergyRS(conn, encounter_ids);
            narrativeRS= getClinNarrativeRS(conn, encounter_ids);
            
            lab_requestRS= getLabRequestRS(conn, encounter_ids);
            test_resultRS= getTestResultRS(conn, encounter_ids);
            referralRS= getReferralRS(conn, encounter_ids);
            encounterTypeRS = getEncounterTypeRS(conn);
            Map vaccineMap = getVaccineMap();
            
            HealthSummary01 hs = new HealthSummaryQuickAndDirty01(
            getDataObjectFactory(),
            new Long(patientId),
            vaccineMap,
            
            healthIssuesRS,
            episodesRS,
            encountersRS,
            vaccinationsRS,
            medicationsRS,
            allergyRS,
            narrativeRS,
            lab_requestRS,
            test_resultRS,
            referralRS,
            encounterTypeRS
            );
            
            
            accessedRecords.put(new Long(patientId),
            getDataObjectFactory().createHealthRecord(hs));
            return (HealthRecord01) accessedRecords.get(new Long(patientId));
            
        } catch (Exception e) {
            throw new org.gnumed.testweb1.persist.DataSourceException(e);
        } finally {
            if (conn != null) {
                try {
                    conn.close();
                } catch (SQLException se) {
                    throw new org.gnumed.testweb1.persist.DataSourceException(se);
                }
            }
            
        }
        
    }
    
    private Map getVaccineMap() throws org.gnumed.testweb1.persist.DataSourceException {
        
        
        Map vaccMap = getClinicalDataAccess().getVaccineMap();
        return vaccMap;
        
        
    }
    
    private long[] getIdsFromResultSet( ResultSet rs, String idName) throws SQLException {
        List l = new ArrayList();
        rs.beforeFirst();
        while (rs.next()) {
            l.add( new Long(rs.getLong(idName) ));
        }
        
        long[] l2= new long[l.size()];
        for (int i =0 ; i < l.size(); ++i) {
            Long lobj = (Long)l.get(i);
            l2[i] = lobj.longValue();
        }
        rs.beforeFirst();
        return l2;
    }
    
    private String idsToString(long[] ids) {
        StringBuffer sb = new StringBuffer();
        for (int i = 0; i <  ids.length; ++i ) {
            if (i > 0) sb.append(',');
            sb.append(Long.toString( ids[i]));
        }
        return sb.toString();
    }
    
    private ResultSet getRowsForIds(Connection conn,  String selectString,
    long[] ids)throws SQLException  {
        
        PreparedStatement stmt =  conn.prepareStatement( selectString +
        ( (ids.length == 0) ? "( null ) " : "("
        + idsToString( ids)+")" ) );
        stmt.execute();
        return stmt.getResultSet();
    }
    
    
    private ResultSet getHealthIssueRS(Connection conn, long patientId)throws SQLException {
        String s = "select "+HEALTH_ISSUE_ATTRIBUTES+" from clin_health_issue hi  where hi.id_patient =  ?" ;
        System.err.println("finding HI :" +s + " for id " + patientId);
        PreparedStatement stmt =  conn.prepareStatement(s);
        stmt.setLong(1, patientId);
        stmt.execute();
        ResultSet rs =  stmt.getResultSet();
        System.err.println("result set = " + rs);
        return rs;
        
    }
    
    
    private ResultSet getClinEpisodesRS(Connection conn,long[] clin_health_issue_ids ) throws SQLException {
        return   getRowsForIds(conn,"select * from clin_episode where fk_health_issue  in",clin_health_issue_ids);
    }
    
    
    private ResultSet getClinEncountersRS(Connection conn, long patientId ) throws SQLException {
        PreparedStatement stmt =  conn.prepareStatement("select * from clin_encounter where fk_patient =  ?   ");
        stmt.setLong(1, patientId);
        stmt.execute();
        return stmt.getResultSet();
        
        
    }
    
    private  ResultSet getEncounterTypeRS( Connection conn  ) throws SQLException {
        PreparedStatement stmt =  conn.prepareStatement("select * from encounter_type");
        stmt.execute();
        return stmt.getResultSet();
        
        
    }
    
    
    private ResultSet getClinRootItemRS(Connection conn,/*String attributeList,*/
    String subtype, long[] encounter_ids) throws SQLException {
        return   getRowsForIds(conn,"select * from "+subtype+" where fk_encounter in ",encounter_ids);
        
    }
    
    private ResultSet getAllergyRS(Connection conn, long[] encounter_ids) throws SQLException{
        return   getClinRootItemRS(conn, /*ALLERGY_ATTRIBUTES,*/ "allergy", encounter_ids);
    }
    
    
    private ResultSet getVaccinationRS(Connection conn, long[] encounter_ids) throws SQLException{
        return   getClinRootItemRS(conn,/*VACCINATION_ATTRIBUTES,*/ "vaccination", encounter_ids);
    }
    
    
    private ResultSet getClinNarrativeRS(Connection conn, long[] encounter_ids) throws SQLException{
        return   getClinRootItemRS(conn,"clin_narrative", encounter_ids);
    }
    
    
    private ResultSet getLabRequestRS(Connection conn, long[] encounter_ids)throws SQLException {
        return   getClinRootItemRS(conn,"lab_request", encounter_ids);
    }
    
    private ResultSet getTestResultRS(Connection conn, long[] encounter_ids)throws SQLException {
        return   getClinRootItemRS(conn,"test_result", encounter_ids);
    }
    
    private ResultSet getReferralRS(Connection conn, long[] encounter_ids) throws SQLException{
        return   getClinRootItemRS(conn,"referral", encounter_ids);
    }
    
    
    private ResultSet getMedicationRS(Connection conn, long[] encounter_ids)throws SQLException {
        return   getClinRootItemRS(conn,"clin_medication", encounter_ids);
    }
    
    private ResultSet getClinDiagRS( Connection conn, long[] clin_narrative_ids) throws SQLException {
        return getRowsForIds(conn, "select * from clin_diag where fk_narrative in ",clin_narrative_ids);
    }
    
    private ClinicalEncounter fromRow(java.sql.ResultSet rs) throws SQLException {
        return null;
    }
    
    
    
    public void save(org.gnumed.testweb1.data.HealthRecord01 healthRecord) throws org.gnumed.testweb1.persist.DataSourceException {
    }
    
    
    
    public javax.sql.DataSource getDataSource() {
        return dataSource;
    }
    
    public void setDataSource(javax.sql.DataSource ds) {
        this.dataSource = ds;
    }
    
    public org.gnumed.testweb1.data.DataObjectFactory getDataObjectFactory() {
        return factory;
    }
    
    public void setDataObjectFactory(org.gnumed.testweb1.data.DataObjectFactory dataObjectFactory) {
        this.factory = dataObjectFactory;
    }
    
    public org.gnumed.testweb1.persist.ClinicalDataAccess getClinicalDataAccess() {
        return clinicalDataAccess;
    }
    
    public void setClinicalDataAccess(org.gnumed.testweb1.persist.ClinicalDataAccess cda) {
        clinicalDataAccess = cda;
    }
    
    /** saves a clinical encounter and it's elements.
     *  ClinNarrative elements which have empty narrative fields are not saved.
     */
    public void save(ClinicalEncounter encounter, HealthSummary01 summary) throws org.gnumed.testweb1.persist.DataSourceException {
        String s1 = "insert into clin_encounter (id, description, started, last_affirmed,  fk_patient) values (?, ?, ?,?,  ? )";
        
        
        String s5 = "insert into vaccination( site, batch_no, clin_when, narrative, soap_cat,  fk_encounter, fk_episode) " +
        "values ( ? , ? , ?, ?, ? , ? , ?)";
        Connection conn = null;
        try {
            conn = getDataSource().getConnection();
            
            conn.setAutoCommit(false);
            
            Integer idEncounter = getNextId(conn, "clin_encounter_id_seq");
            
            encounter.getDescription();
            
            java.util.Date started = nullToNow(encounter.getStarted());
            java.util.Date affirmed = nullToNow(encounter.getLastAffirmed());
            
            PreparedStatement insertEncounter = conn.prepareStatement(s1);
            insertEncounter.setObject(1,idEncounter);
            insertEncounter.setString(2, encounter.getDescription());
            insertEncounter.setTimestamp(3,  new java.sql.Timestamp(started.getTime()) );
            insertEncounter.setTimestamp(4,new java.sql.Timestamp( affirmed.getTime()));
            insertEncounter.setObject(5, summary.getIdentityId());
            insertEncounter.execute();
            
            encounter.setId(new Long(idEncounter.longValue()));
            
            
            
            
            
            List healthIssues = new ArrayList();
          
            
           ClinRootItem[] items=encounter.getRootItems();
           
           for( int i=0; i < items.length;++i) {
                if (items[i].getNarrative() ==null || items[i].getEpisode().getDescription() ==null)
                {
                    log.info("null narrative or episode description: SKIPPING " + items[i]);
                    continue;
                }
                
                if (items[i].getNarrative().trim().equals("") )
                    continue;
                
                String healthIssueName   =normalizeHealthIssueName( items[i]);
                HealthIssue issue = findOrCreateHealthIssue(conn, healthIssueName, summary);
                healthIssues.add(issue);
                
                ClinicalEpisode episode = findOrCreateEpisode( conn, issue, items[i].getEpisode() );
                
                items[i].setEpisode(episode);
            }  
           
            List[] itemLists = new java.util.List[] {
                encounter.getNarratives(), encounter.getAllergies()
            };
            
            for (int j = 0; j < itemLists.length; ++j) {
                for( java.util.ListIterator i = itemLists[j].listIterator(); i.hasNext(); ) {
                    ClinRootItem item = (ClinRootItem) i.next();
                    if (item.getNarrative() == null || item.getNarrative().trim().equals("") ||
                    item.getEpisode().getDescription() == null ) {
                        // DONT SAVE EMPTY itemS
                        log.info("** REMOVE ** " + item );
                        log.info(" episode.description=" + item.getEpisode().getDescription());
                        log.info("*********** has null narrative or null episode description");
                        
                        i.remove();
                    }
                }
            }
                  
            for( Iterator i = encounter.getNarratives().iterator(); i.hasNext(); ) {
                ClinNarrative narrative = (ClinNarrative) i.next();
                 
                saveNarrative(conn, narrative);
            }
            
            for( Iterator i = encounter.getAllergies().iterator(); i.hasNext(); ) {
                saveAllergy(conn, (Allergy) i.next() );
            }
            
            conn.commit();
            conn.close();
            
            HealthRecord01 hr =(HealthRecord01) getAccessedRecords().get(summary.getIdentityId());
            
            Iterator k = healthIssues.iterator();
            while (k.hasNext()) {
                HealthIssue issue = (HealthIssue) k.next();
                
                if ( !hr.getHealthSummary().hasHealthIssue(issue) ) {
                    hr.getHealthSummary().addHealthIssue(issue);
                }
            }
            
        } catch (Exception exception) {
            try {
                conn.rollback();
                conn.close();
            } catch (Exception e2) {
                e2.printStackTrace();
            }
            throw new DataSourceException("unexpected ", exception);
        }
        
        
        
    }
    
    /** gets the next id from the sequence named */
    private Integer getNextId(Connection conn, String seqName) throws DataSourceException , SQLException {
        Statement stmt = conn.createStatement();
        stmt.execute("select nextval ('"+seqName+"')");
        ResultSet rs = stmt.getResultSet();
        Integer id = null;
        while(rs.next()) {
            id= new Integer(rs.getInt(1));
        }
        if (id == null)
            throw new DataSourceException("id from "+ seqName + " was null");
        return id;
    }
    
    /** makes healthissue name non-null, default xxxDEFAULTxxxx */
    private String normalizeHealthIssueName(ClinRootItem item) {
        
        String healthIssueName = item.getEpisode().getHealthIssue().getDescription();
        String newName = item.getNewHealthIssueName();
       
        healthIssueName = healthIssueName == null ? "" : healthIssueName;
        newName = ( newName == null ? "" : newName);
        
        if (!newName.equals("") && healthIssueName.equals("")) {
            healthIssueName = newName;
        }
        
        if (healthIssueName.equals("")) {
            healthIssueName = Constants.Schema.DEFAULT_HEALTH_ISSUE_LABEL;
        }
        
        return healthIssueName;
    }
    
    
    private ClinicalEpisode findOrCreateEpisode( Connection conn, HealthIssue issue, ClinicalEpisode candidateEpisode) throws DataSourceException, SQLException {
        
        ClinicalEpisode[] episodes = issue.getClinicalEpisodes();
        
        for (int i =0; i < episodes.length; ++i ) {
            log.info("episodes[i].description=" + episodes[i].getDescription()
            + "   candidateEpisodes=" + candidateEpisode.getDescription());
            if( isSameEpisode(episodes[i], candidateEpisode ) ) {
                
                return episodes[i];
            }
        }
        
        
        
        Integer id = getNextId(conn, "clin_episode_pk_seq");
        
        
        String s3b = "insert into clin_episode( pk, description, fk_health_issue) values( ? , ?, ?)";
        PreparedStatement stmt = conn.prepareStatement(s3b);
        
        stmt.setInt( 1, id.intValue());
        stmt.setString(2, candidateEpisode.getDescription());
        stmt.setInt(3, issue.getId().intValue());
        
        stmt.execute();
        
        candidateEpisode.setId(new Long(id.longValue()));
        candidateEpisode.setHealthIssue(issue);
        issue.setClinicalEpisode( issue.getClinicalEpisodes().length , candidateEpisode);
        
        return candidateEpisode;
        
    }
    
    
    private boolean isSameEpisode( ClinicalEpisode e1, ClinicalEpisode e2) {
        
        return Algorithms.isCharMatchedInWords(e1.getDescription(), e2.getDescription(), WORD_THRESHOLD, MATCHED_WORDCOUNT_THRESHHOLD)
        && java.lang.Math.abs(e1.getModified_when().getTime() - e2.getModified_when().getTime()) < SAME_EPISODE_INTERVAL;
    }
    
    
    private HealthIssue findOrCreateHealthIssue(Connection conn,String healthIssueName, HealthSummary01 summary) throws DataSourceException, SQLException {
        // hacky guard
        if (healthIssueName.trim().equals(""))
            healthIssueName = "xxxDEFAULTxxx";
        
        
        Iterator i = summary.getHealthIssues().iterator();
        while (i.hasNext()) {
            HealthIssue hi = (HealthIssue) i.next();
            if ( Algorithms.
            isCharMatchedInWords(
            hi.getDescription().toLowerCase() , healthIssueName.toLowerCase(),
            WORD_THRESHOLD, MATCHED_WORDCOUNT_THRESHHOLD) )
                
            {
                log.info( "Matched " + hi.getDescription().toLowerCase() + " with " + healthIssueName.toLowerCase() );
                return hi;
            }
        }
        
        log.info("New health issue is " + healthIssueName + " identity id = " + summary.getIdentityId());
        Integer id = getNextId(conn, "clin_health_issue_id_seq");
        String s2b = "insert into clin_health_issue(id, id_patient, description) values( ?,?,?)";
        PreparedStatement stmt = conn.prepareStatement(s2b);
        stmt.setInt(1,id.intValue());
        stmt.setInt(2, summary.getIdentityId().intValue());
        stmt.setString(3, healthIssueName);
        stmt.execute();
        
        HealthIssue hi = getDataObjectFactory().createHealthIssue();
        hi.setId( new Long( id.longValue()));
        hi.setDescription(healthIssueName);
        summary.getHealthIssues().add(hi);
        
        
        
        return hi;
        
        
    }
    
    private void saveNarrative( Connection conn, ClinNarrative narrative) throws DataSourceException, SQLException {
        String s4 = "insert into clin_narrative(pk_item, is_aoe, is_rfe, clin_when, narrative, soap_cat,  fk_encounter, fk_episode) " +
        "values (?,  ? , ? , ?, ?, ? , ? , ? )";
        
        PreparedStatement stmt = conn.prepareStatement(s4);
        stmt.setBoolean(2, narrative.isAoe());
        stmt.setBoolean(3, narrative.isRfe());
        
        setClinRootItemStatement( stmt, narrative, 4);
        
        log.info(s4);
        
        stmt.execute();
        
    }
    
    private void setClinRootItemStatement(PreparedStatement stmt, ClinRootItem item, int startIndex) throws DataSourceException, SQLException {
        
        Integer id = getNextId(stmt.getConnection(), "clin_root_item_pk_item_seq");
        
        stmt.setInt(1, id.intValue());
        stmt.setTimestamp(startIndex++, new java.sql.Timestamp( item.getClin_when().getTime() ));
        stmt.setString(startIndex++, item.getNarrative() == null ? "": item.getNarrative() );
        
        
        stmt.setString(startIndex++, item.getSoapCat().substring(0,1) );
        stmt.setInt(startIndex++, item.getEncounter().getId(). intValue() );
        stmt.setInt(startIndex++,   item.getEpisode().getId(). intValue() );
        
    }
    
    private void saveAllergy( Connection conn, Allergy allergy) throws DataSourceException, SQLException {
        log.info( "SAVE ALLERGY" + allergy.getEncounter() +":"+allergy.getNarrative()+":" + allergy.getSubstance());
       
        if (allergy.getEncounter() == null || allergy.getEpisode() == null) {
            log.info("DIDNot save");
            return;
        }
        String s5 = "insert into allergy(pk_item, definite, substance,id_type,   clin_when, narrative, soap_cat,  fk_encounter, fk_episode) " +
        "values (?,  ? , ? , ?, ?, ? , ? , ?, ?)";
        
        log.info( "SAVE ALLERGY" + allergy.getEncounter() +":"+allergy.getNarrative()+":" + allergy.getSubstance());
        
        PreparedStatement stmt = conn.prepareStatement(s5);
      
        setClinRootItemStatement( stmt, allergy, 5);
        
        stmt.setInt(4,1); // id_type allergy 
       //  ** change **
        
        stmt.setString(3, allergy.getSubstance());
        
        stmt.setBoolean(2, allergy.isDefinite());
        
        log.info(s5);
        stmt.execute();
    }
    
    private java.util.Date nullToNow(java.util.Date d) {
        if (d == null)
            return new java.util.Date();
        return d;
        
    }
    
    
    private void ensureXLinkIdentityExists(Connection conn,long patientId) throws SQLException {
        String s8 = "select xfk_identity from xlnk_identity where xfk_identity=  ?";
        PreparedStatement stmt = conn.prepareStatement(s8);
        stmt.setLong(1, patientId);
        stmt.execute();
        ResultSet rs = stmt.getResultSet();
        if (rs.next()) {
            stmt.close();
            return;
        }
        String s9= "insert into xlnk_identity( xfk_identity, pupic) values( ? , ?)";
        PreparedStatement stmt2 = conn.prepareStatement(s9);
        stmt2.setLong(1, patientId);
        stmt2.setLong(2, patientId);
        stmt2.execute();
        
        stmt2.close();
    }
}
