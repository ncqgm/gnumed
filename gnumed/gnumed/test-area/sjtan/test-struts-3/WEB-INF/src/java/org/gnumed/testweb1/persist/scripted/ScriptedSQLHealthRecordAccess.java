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
import java.sql.*;
import java.util.*;
/**
 *
 * @author  sjtan
 */
public class ScriptedSQLHealthRecordAccess implements
HealthRecordAccess01, DataSourceUsing, DataObjectFactoryUsing  {
    javax.sql.DataSource dataSource;
    org.gnumed.testweb1.data.DataObjectFactory factory;
    Map accessedRecords = new HashMap();
    
    /** change the fields for aliasing , if field names change
     */
    
   private org.gnumed.testweb1.persist.ClinicalDataAccess clinicalDataAccess;
    
    private static final String HEALTH_ISSUE_ATTRIBUTES = "hi.id as id, hi.description as description ";
    private static final String CLIN_EPISODE_ATTRIBUTES = "id as id, modified_when as modified_when, description as description";
    private static final String CLIN_ROOT_ITEM_ATTRIBUTES= "pk_item as id, clin_when as clin_when , soap_cat as soap_cat, narrative as narrative";
    private static final String CLIN_NARRATIVE_ATTRIBUTES = CLIN_ROOT_ITEM_ATTRIBUTES + ", is_rfe as is_rfe, is_aoe as is_aoe";
    
    
    /** Creates a new instance of ScriptedSQLHealthRecordAccess */
    public ScriptedSQLHealthRecordAccess() {
    }
    
    public HealthRecord01 findHealthRecordByIdentityId(long patientId) throws org.gnumed.testweb1.persist.DataSourceException {
        
        synchronized(this) {
            if (accessedRecords.containsKey(new Long(patientId)) ) {
                return (HealthRecord01) accessedRecords.get(new Long(patientId));
                
            }
        }
        
        try {
        Connection conn = dataSource.getConnection();
        conn.setReadOnly(true);
        
        
        
        ResultSet healthIssuesRS, episodesRS, encountersRS,
        vaccinationsRS, medicationsRS, allergyRS, narrativeRS,
        lab_requestRS, test_resultRS, referralRS;
        
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
        Map vaccineMap = getVaccineMap();
        
        HealthSummary01 hs = new HealthSummaryQuickAndDirty01(
        getDataObjectFactory(),
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
        referralRS
        );
        
        synchronized (this ){
            accessedRecords.put(new Long(patientId),
            getDataObjectFactory().createHealthRecord(hs));
            return (HealthRecord01) accessedRecords.get(new Long(patientId));
        }
        } catch (Exception e) {
            throw new org.gnumed.testweb1.persist.DataSourceException(e);
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
        return   getClinRootItemRS(conn,"curr_medication", encounter_ids);
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
    
}
