from pyjamas.builder.Builder import Builder, HTTPUILoader
import GMWevents

#======================================================
class cPatientSelector: 
    """ Patient Selector.
        
    """
    def __init__(self, patients):
        self.ps = None
        self.patients = patients
        HTTPUILoader(self).load("gnumedweb.xml") # calls onUILoaded when done

    #--------------------------------------------------
    def onUILoaded(self, text):
        self.b = Builder(text)
        self.ps = self.b.createInstance("PatientSelect", self)
        self.fill_grid()
        self.ps.centerBox()
        self.ps.show()

    #--------------------------------------------------
    def getPanel(self):
        return self.ps

    #--------------------------------------------------
    def fill_grid(self):
        grid = self.ps.vp.sp.grid
        grid.resize(1+len(self.patients), 3)
        for (row, patient) in enumerate(self.patients):
            grid.setHTML(row+1, 0, patient.description)
            grid.setHTML(row+1, 1, patient.formatted_dob)
            grid.setHTML(row+1, 2, patient.xmin_identity)
                
    #--------------------------------------------------
    def onPatientCellClicked(self, sender, row, col):
        if row == 0:
            return
        patient = self.patients[row-1]
        GMWevents.events.onPatientSelectedEvent(self, patient)
        self.ps.hide()

    #--------------------------------------------------
    def onPatientSelectOk(self, sender):
        self.ps.hide()

    #--------------------------------------------------
    def onPatientSelectCancel(self, sender):
        self.ps.hide()

