/*
 * Created on 21-Oct-2004
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.adapters;
 
import org.gnumed.testweb1.persist.ConfigurableHealthRecordAccess;
import org.gnumed.testweb1.persist.scripted.gnumed.ClinRootInsert;
import org.gnumed.testweb1.persist.scripted.gnumed.MedicationSaveScript;
import org.gnumed.testweb1.persist.scripted.gnumed.clinroot.ClinRootInsertV01;
import org.gnumed.testweb1.persist.scripted.gnumed.medication.MedicationSaveScriptV02;

/**
 * @author sjtan
 *
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
public class HealthRecordAccessConfigurationV02 implements HealthRecordAccessConfiguration {

	 
	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.adapters.HealthRecordAccessConfiguration#configure(org.gnumed.testweb1.persist.scripted.ConfigurableHealthRecordAccess)
	 */
	public void configure(ConfigurableHealthRecordAccess access) {
		 access.setClinRootInsert( new ClinRootInsertV01());
		 access.setMedicationSave(new MedicationSaveScriptV02());
		 
	}

}
