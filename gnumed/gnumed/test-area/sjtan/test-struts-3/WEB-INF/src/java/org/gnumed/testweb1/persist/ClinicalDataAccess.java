/*
 * ClinicalDataAccess.java
 *
 * Created on July 5, 2004, 7:35 PM
 */

package  org.gnumed.testweb1.persist;
import java.util.List;
import org.gnumed.testweb1.persist.DataSourceException;
import org.gnumed.testweb1.data.Vaccination;
/**
 *
 * @author  sjtan
 */
public interface ClinicalDataAccess {
    public List getVaccines() throws DataSourceException;
    public void updateVaccinations(Long patientId, Vaccination[] vaccinations) throws DataSourceException;
}
