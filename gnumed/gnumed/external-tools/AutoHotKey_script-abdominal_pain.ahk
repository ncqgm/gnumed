::abdominalpain::
#NoEnv
Gui, Destroy
Gui, Add, Text, ,How long is the  abdominal pain?
Gui, Add, Edit, vHowLong
Gui, Add, Text, ,What is the site of pain?
Gui, Add, ListBox, vLocation1, diffuse|right|left|center
Gui, Add, ListBox, vLocation2,  Upper abdomen|Lower abdomen|periumbilical|flanks|poorly localised
Gui, Add, Text, , How was the onset of pain?
Gui, Add, DropDownList, vOnset, instantaneously|suddenly|Gradually
Gui, Add, Text, ,what is the periodicity of pain?
Gui, Add, DropDownList, vPeriodicity, pain Occured once only|had continuous|had recurrent
Gui, Add, Text, ,If recurrent, what is the frequency?
Gui, Add, DropDownList, vRecurrent,  every few minutes|every few hours|every day at least once| every alternate day|two to three times every week|once or twice a month|once in 3-6 months|once in a year
Gui, Add, Text, ,What are aggravating factors?
Gui, Add, ListBox, , vAggrfactors,  Nothing|Food|defecation|urination|movement|respiration|drugs
Gui, Add, Text, ,What relieves pain?
Gui, Add, ListBox, , vRelfactors,  Nothing|Food|defecation|urination|movement|respiration|drugs|vomitings
Gui, Add, Text, ,Which drug relieves pain?
Gui, Add, Edit, vDrug
Gui, Add, Text, ,When was the last episode?
Gui, Add, Edit, vLastEpisode
Gui, Add, Button, ,Submit
Gui, Show

Return

ButtonSubmit:
Gui, Submit

SendInput, Patient had pain in the %vLocation1% %Location2% for %HowLong%. Pain started %Onset%. Periodicity: %Periodicity% . Patient had pain %Recurrent%. %Aggrfactors% increasedpain. %Relfactors%  %Drug% relieved pain. The last episode occured %LastEpisode%
Gui, Submit


Return

GuiClose:
ExitApp




