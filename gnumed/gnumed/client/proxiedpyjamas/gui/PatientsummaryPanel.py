from pyjamas.ui.StackPanel import StackPanel
from pyjamas.ui.HTML import HTML

from ProviderInboxPanel import cProviderInboxPanel
from PatientInboxPanel import cPatientInboxPanel

class cPatientsummaryPanel(StackPanel):
    def __init__(self):
        StackPanel.__init__(self, Width="100%", Height="300px")

        self.add(cProviderInboxPanel(), "Inbox")
        self.add(cPatientInboxPanel(), "Patient Messages")
        self.add(HTML('The<br>early<br>bird<br>catches<br>the<br>worm.'),
                  "Waiting list")
        self.add(HTML('The smart money<br>is on the<br>black horse.'),
                  "Demographic and identity")
        self.add(HTML('The smart money<br>is on the<br>black horse.'),
                  "Hospitalization (most recent known)")
        self.add(HTML('The smart money<br>is on the<br>black horse.'),
                  "Operation (most recent known)")
        self.add(HTML('The smart money<br>is on the<br>black horse.'),
                  "Allergies and intolerances (known)")
        self.add(HTML('The smart money<br>is on the<br>black horse.'),
                  "Medication, current (known)")
        self.add(HTML('The smart money<br>is on the<br>black horse.'),
                  "Medication, discontinued (known, past 120 days)")
        self.add(HTML('The smart money<br>is on the<br>black horse.'),
                  "Problem list")
 
