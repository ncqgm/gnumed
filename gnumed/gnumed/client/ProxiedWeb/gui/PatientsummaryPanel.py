from pyjamas.ui.SimplePanel import SimplePanel
from pyjamas.ui.StackPanel import StackPanel
from pyjamas.ui.HTML import HTML

class cPatientsummaryPanel(SimplePanel):
    def __init__(self, app):
        self.app = app
        SimplePanel.__init__(self)

        stack = StackPanel(Width="100%", Height="300px")

        stack.add(HTML('The quick<br>brown fox<br>jumps over the<br>lazy dog.'),
                  "Inbox")
        stack.add(HTML('The<br>early<br>bird<br>catches<br>the<br>worm.'),
                  "Waiting list")
        stack.add(HTML('The smart money<br>is on the<br>black horse.'),
                  "Demographic and identity")
        stack.add(HTML('The smart money<br>is on the<br>black horse.'),
                  "Hospitalization (most recent known)")
        stack.add(HTML('The smart money<br>is on the<br>black horse.'),
                  "Operation (most recent known)")
        stack.add(HTML('The smart money<br>is on the<br>black horse.'),
                  "Allergies and intolerances (known)")
        stack.add(HTML('The smart money<br>is on the<br>black horse.'),
                  "Medication, current (known)")
        stack.add(HTML('The smart money<br>is on the<br>black horse.'),
                  "Medication, discontinued (known, past 120 days)")
        stack.add(HTML('The smart money<br>is on the<br>black horse.'),
                  "Problem list")
 
        self.add(stack)