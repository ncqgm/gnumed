/*
 * Created on 27-Feb-2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.forms;

import java.util.ArrayList;
import java.util.List;

import org.gnumed.testweb1.data.HealthIssue;
import org.gnumed.testweb1.data2.EntryClinicalEpisode;
import org.gnumed.testweb1.data2.EntryClinicalEpisodeImpl1;

/**
 * @author sjtan
 * 
 * TODO To change the template for this generated type comment go to Window -
 * Preferences - Java - Code Style - Code Templates
 */
public class ClinicalFormFactory2 extends AbstractClinicalFormFactory implements
        IClinicalFormFactory {

    /*
     * (non-Javadoc)
     * 
     * @see org.gnumed.testweb1.forms.IClinicalFormFactory#getClinicalUpdateForm()
     */
    public BaseClinicalUpdateForm getClinicalUpdateForm() {
        // TODO Auto-generated method stub
        ClinicalUpdateForm2 form2 = new ClinicalUpdateForm2();
        for (int i = 0; i < GetEntryEpisodeCount(); ++i) {
            addEntryEpisode(form2);
        }

        return form2;
    }

    /**
     * @param form2
     */
    private void addEntryEpisode(ClinicalUpdateForm2 form2) {
        // TODO Auto-generated method stub

        if (form2.getEntryClinicalEpisodes() == null) {
            form2
                    .setEntryClinicalEpisodes(new EntryClinicalEpisode[GetEntryEpisodeCount()]);
        }

        EntryClinicalEpisode episode = new EntryClinicalEpisodeImpl1();

        initEpisode(episode);

        form2.setEntryClinicalEpisode(form2.getEntryClinicalEpisodes().length,
                episode);

    }

    private void initEpisode(EntryClinicalEpisode episode) {
        HealthIssue issue = getDataObjectFactory().createHealthIssue();
        episode.setHealthIssue(issue);

        addAllergies(episode);

        addVaccs(episode);

        addNarratives(episode);

        addMeds(episode);

        episode.setDefiningNarrative( getDataObjectFactory().createClinNarrative());
    }

    /**
     * @param episode
     */
    private void addAllergies(EntryClinicalEpisode episode) {
        int nAllergy = 4;

        List l = new ArrayList();

        for (int i = 0; i < nAllergy; ++i) {
            l.add(getDataObjectFactory().createAllergy());
        }
        episode.setAllergys(l);
    }

    /**
     * @param episode
     */
    private void addNarratives(EntryClinicalEpisode episode) {
        List l;
        l = new ArrayList();
        int nNarratives = 8;

        for (int i = 0; i < nNarratives; ++i) {
            l.add(getDataObjectFactory().createClinNarrative());
        }

        episode.setClinNarratives(l);
    }

    /**
     * @param episode
     */
    private void addMeds(EntryClinicalEpisode episode) {
        List l;
        l = new ArrayList();

        int nMeds = 10;

        for (int i = 0; i < nMeds; ++i) {

            l.add(getDataObjectFactory().createEntryMedication());

        }

        episode.setMedications(l);
    }

    /**
     * @param episode
     */
    private void addVaccs(EntryClinicalEpisode episode) {
        List l;
        int nVaccs = 8;
        l = new ArrayList();

        for (int i = 0; i < nVaccs; ++i) {
            l.add(getDataObjectFactory().createVaccination());
        }

        episode.setVaccinations(l);
    }
}