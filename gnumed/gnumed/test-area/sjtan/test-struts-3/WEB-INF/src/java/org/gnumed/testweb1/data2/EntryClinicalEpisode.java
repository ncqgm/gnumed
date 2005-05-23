/*
 * Created on 07-Feb-2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.data2;

import java.util.List;

import org.gnumed.testweb1.data.Allergy;
import org.gnumed.testweb1.data.ClinNarrative;
import org.gnumed.testweb1.data.ClinRootItem;
import org.gnumed.testweb1.data.ClinicalEpisode;
import org.gnumed.testweb1.data.HealthIssue;
import org.gnumed.testweb1.data.Medication;
import org.gnumed.testweb1.data.Vaccination;
import org.gnumed.testweb1.data.Vitals;

/**
 * @author sjtan
 *
 * provides an entry format where clin root items are organized under
 * episodes.
 * 
 */
public interface EntryClinicalEpisode extends ClinicalEpisode {
    public boolean isLastEpisodeCloseable();
    public boolean isLastEpisodeOpenable();
    
    public boolean isOpeningLastEpisode();
    public void setOpeningLastEpisode(boolean open);
    
    public boolean isClosingLastEpisode();
    
    public void setClosingLastEpisode(boolean close);
    
    public void setLastEpisode(ClinicalEpisode episode);
    public ClinicalEpisode getLastEpisode();
    
    public void setHealthIssue(HealthIssue issue);
    public HealthIssue getHealthIssue();
    
    public  void setNarratedDescription(boolean narrated);
    public boolean isNarratedDescription();
    
    public ClinNarrative getDefiningNarrative();
    public void setDefiningNarrative(ClinNarrative narrative);
    public void setClinNarrative(int i, ClinNarrative n);
    public ClinNarrative getClinNarrative(int i);
    public List getClinNarratives();
    
    public void setClinNarratives(List l);
    
    public void setVitals(List l);
    public void setVital( int i, Vitals v);
    public Vitals getVital(int i);
    public List getVitals();
    
    public void setMedications(List l);
    public void setMedication(int i, Medication med);
    public Medication getMedication(int i);
    public List getMedications();
    
    public void setVaccinations(List l);
    public void setVaccination( int i, Vaccination vacc);
    public Vaccination getVaccination(int i);
    public List getVaccinations();
    
    public void setAllergys(List l);
    public void setAllergy(int i, Allergy a);
    public Allergy getAllergy(int i);
    public List getAllergys();
    
    
    
}