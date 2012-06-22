::abdominalpain::
#NoEnv
Gui, Destroy

Gui, Add, Text, x16 y10 w400 h30 , duration of abdominal pain
Gui, Add, Edit, x16 y50 w400 h30 r1 vDurationofabdominalpain, Edit
Gui, Add, Text, x16 y90 w400 h30 , Pattern of abdominal pain
Gui, Add, DropDownList, x16 y130 w400 h20 vPatternofabdominalpain, recurrent | continuous | periodic
Gui, Add, Text, x16 y160 w400 h30 , if periodic, what is the frequency?
Gui, Add, Edit, x16 y200 w400 h30 vFrequencyofabdominalpain, Edit
Gui, Add, Text, x16 y240 w400 h30 , When was the last episode?
Gui, Add, Edit, x16 y280 w400 h30 vLastepisodeofabdominalpain, Edit
Gui, Add, Text, x16 y320 w400 h30 , What is the site of abdominal pain?
Gui, Add, ListBox, x16 y360 w410 h170 vSiteofabdominalpain, right hypochondriac | epigastric |left hypochondriac |left paraumbilical|periumbilical|right paraumbilical|left iliac fossa|hypogastric|right iliac fossa| upper abdomen| lower abdomen| diffuse|poorly localised
Gui, Add, Text, x16 y530 w410 h30 , Radiation ?
Gui, Add, DropDownList, x16 y570 w410 h20 vRadiationofpain, No radiation | Pain radiates to back| Pain radiates to shoulder | Pain radiates to scapula | Pain radiates anteriorly to thigh | Pain radiates to tip of penis | Pain radiates anteriorly from loin to groin
Gui, Add, Text, x16 y600 w410 h30 , What is the character of pain?
Gui, Add, ListBox, x16 y640 w410 h120 vCharacterofabdominalpain, burning | dull ache | sharp shooting| crampy |colicky | poorly described|
Gui, Add, Text, x486 y10 w360 h30 , How long the pain episodes persisted?
Gui, Add,ListBox, x486 y50 w360 h30 vDurationofpainepisode, Last few seconds to a minute | lasted few minutes | lasted few hours | lasted  a day | pain is continuous and patient is still in agony.
Gui, Add, Text, x486 y90 w360 h30 , What is perceived severity of pain?
Gui, Add, DropDownList, x486 y130 w360 h40 vSeverityofabdominalpain, Mild | Moderate- does not disturb routine activity/sleep | severe- patient cannot carry out any day to day activity due to pain.
Gui, Add, Text, x486 y160 w360 h30 , What are aggraveating factors?
Gui, Add, ListBox, x486 y200 w360 h160 Multi vAggravatingfactorsforabdominalpain, meals |motion | micturition | movement| menses | medication | respiration | exertion | standing | coughing | medication
Gui, Add, Text, x486 y370 w360 h30 , What are relieving factors?
Gui, Add, ListBox, x486 y410 w360 h150 Multi vRelievingfactorsforabdominalpain, meals | motion | micturition | movement | menses| medication | respiration | exertion | standing | coughing | medication
Gui, Add, Text, x486 y640 w360 h30 , Any other relevant information?
Gui, Add, Edit, x486 y680 w360 h40 r3 vInformationofabdominalpain, Edit
Gui, Add, Button, x606 y730 w130 h40 , Submit
Gui, Add, Text, x16 y760 w410 h30 , How was the onset and progression of pain?
Gui, Add, Edit, x16 y800 w420 h30 vOnsetprogressionofabdominalpain, Edit
;
Gui, Show

Return



ButtonSubmit:
Gui, Submit

SendInput, Patient complained of abdominal pain since %Durationofabdominalpain%. The pain was %Patternofabdominalpain%. It occurred %Frequencyofabdominalpain%. The most recent episode occurred %Lastepisodeofabdominalpain%. The pain is %Siteofabdominalpain% in location. %Radiationofpain%. Pain is %Characterofabdominalpain% in character.%Onsetprogressionofabdominalpain%.  During an episode,  pain on average %Durationofpainepisode%. Pain usually is %Severityofabdominalpain%. The %Aggravatingfactorsforabdominalpain% worsens pain, while pain is relieved by %Relievingfactorsforabdominalpain%. %Informationofabdominalpain%
Gui, Submit


Return

GuiClose:
ExitApp

