#!/usr/bin/python
#############################################################################
#
# gmLabels: labelling GNUMed's list box controls
# ---------------------------------------------------------------------------
#
# listbox control labels can be defined here centrally.
# The number of columns in a list box control will
# be set by the number of labels.

# Some of the list controls will be labelled automatically
# depending on their column labels within the database; however
# we encourage to rather list the labels here centrally
# future versions will build this module "ad-hoc" from the database
# for now, this will do to facilitate development of other modules
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
# @change log:
#	30.08.2001 hherb initial implementation, untested
#	02.11.2001 commenting of source, mino changes
#
# @TODO:
#	- all runtime error checking / exception handling
#	- test function
############################################################################

"""gmLabels: labelling GNUMed's list box controls"""

if __name__ == '__main__':
	_ = lambda x:x

from wxPython.wx import *

Patients = (_("lastname"), _("firstnames"), _("called"), _("d.o.b"), _("street"), _("city"), _("urid"))
Imphx = (_("date"), _("problem"), _("resolved"), _("treatment"))
Currx = (_("date"), _("problem"), _("treatment"))
Communication = (_("device"), _("at"), _("number"))
Cards = (_('Card type'), _('number'), _('valid'), _('issuer'))
Summaryrx = (_('Drug'), _('strength'), _('dose'))
Summaryhx = (_('Date'), _('problem'), _('resolved'))
Recalls = (_('date'), _('timeframe'),_('reason'))
Debuglog = (_('Timestamp'), _('user'), _('log message'))
ICD10 = (_("code"), _("text"))
CodebrowserActiveProbs = (_('date'), _('code'), _('problem'))
CodebrowserPastMHx = (_('date'), _('code'),  _('problem'))


def LabelListControl(listctrl, labellist):
    """Set the labels of a list box control

    listctrl: a wxListCtrl
    labellist: a list of strings
    """
    for i in range(len(labellist)):
        listctrl.InsertColumn(i, labellist[i])
    #listctrl.SetSingleStyle(wxLC_VRULES)
    #listctrl.SetSingleStyle(wxLC_HRULES)


if __name__ == "__main__":
	print "This module has no test function yet. Please write it"
