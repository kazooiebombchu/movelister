"""
Main entry file for the whole project for both LibreOffice UI and a command-line interface.

For LibreOffice this file contains all runnable Python macros which can be
attached to key combinations or buttons on the sheet. For command-line
interface this file will connect to a running LibreOffice process using socket
and execute this file as a normal Python script. The command-line interface is
mainly useful during the development. It enables running and debugging macros
from the command-line without using LibreOffice.
"""
import uno # noqa
import os
import sys

from unohelper import fileUrlToSystemPath

# This will modify path to include movelister module be part of it. This is
# needed because this file is the main entry to the program and it can be
# executed from three different contexts: from command-line, from LibreOffice
# when macros are part of the system files and from LibreOffice when movelister
# source files are packed inside LibreOffice document for release.
if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname('__file__'), 'pythonpath'))
elif __name__ == 'ooo_script_framework': # Name when executed from LibreOffice.
    # When executed from LibreOffice, add Python files inside to the document
    # be part of the system path so they can be imported normally.
    doc = XSCRIPTCONTEXT.getDocument()
    url = fileUrlToSystemPath('{}/{}'.format(doc.URL,'Scripts/python/pythonpath'))
    sys.path.insert(0, url)

from movelister.core import cursor, names, errors  # noqa
from movelister.core.namedRanges import NamedRanges
from movelister.core.context import Context # noqa
from movelister.format import action, overview # noqa
from movelister.format.details import DetailsFormatter # noqa
from movelister.format.overview import OverviewFormatter # noqa
from movelister.process.updateOverview import UpdateOverview # noqa
from movelister.process.updateDetails import UpdateDetails # noqa
from movelister.process import conditionalFormat # noqa
from movelister.process.updateStyles import UpdateStyles # noqa
from movelister.sheet import helper # noqa
from movelister.sheet.about import About # noqa
from movelister.sheet.details import Details # noqa
from movelister.sheet.master import Master # noqa
from movelister.sheet.modifiers import Modifiers # noqa
from movelister.sheet.overview import Overview # noqa
from movelister.sheet.results import Results # noqa
from movelister.sheet.inputs import Inputs
from movelister.sheet.sheet import Sheet, MASTER_LIST_SHEET_NAME # noqa
from movelister.sheet.sheet import MODIFIER_LIST_SHEET_NAME, ABOUT_SHEET_NAME, RESULT_LIST_SHEET_NAME, INPUT_LIST_SHEET_NAME # noqa
from movelister.ui import message_box  # noqa
from movelister.utils import format, validation, version # noqa

# Setup context automatically when macro is run from the LibreOffice.
if __name__ != '__main__':
    Context.setup()


def updateDetails(*args, **kwargs):
    """
    A macro function that will update one Details-sheet while preserving
    previous user data. Movelister can have multiple Details-views. To determine
    which one is updated, the code checks which Overview button was pressed to
    trigger the macro.
    """
    try:
        if not Sheet.checkTemplatesExists():
            message_box.showWarningWithOk('This file doesn\'t seem to have all necessary templates. Can\'t generate.')
            return

        # Get Overview sheet name from active sheet or from provided kwargs.
        activeOverviewName = kwargs.get('activeSheet', helper.getActiveSheetName())
        # Get view name for the Details. This is presented in Overview sheet name inside parentheses.
        viewName = names.getViewName(activeOverviewName)
        detailsSheetName = names.getDetailsName(viewName)
        previousDetails = Details(viewName)
        if Sheet.hasByName(detailsSheetName):
            # Check if user wants to update existing Details-sheet.
            if not message_box.showSheetUpdateWarning():
                return
            previousDetails = Details.fromSheet(detailsSheetName)
        modifiersSheet = Modifiers(MODIFIER_LIST_SHEET_NAME)
        parentOverview = Overview.fromSheet(activeOverviewName)
        # Create new Details sheet by combining new and existing data.
        newDetails = UpdateDetails.update(modifiersSheet, parentOverview, previousDetails, viewName)
        # Delete previous Details-sheet and generate a new one.
        Sheet.deleteSheetByName(detailsSheetName)
        formatter = DetailsFormatter(newDetails, parentOverview)
        unoDetailsSheet = formatter.generate()
        # Make columns width optimal.
        length = cursor.getWidth(unoDetailsSheet)
        format.setOptimalWidthToRange(unoDetailsSheet, 0, length)
        # Generate data validation.
        validation.setDataValidationToDetailsSheet(unoDetailsSheet, viewName)
        # Generate named ranges.
        about = About(ABOUT_SHEET_NAME)
        if about.isGenerateNamedRangesOn():
            NamedRanges(unoDetailsSheet, 0, viewName).generate()
        # Generate cell styles used for details sheet.
        UpdateStyles.update()
        # Create conditional format ranges to the new details sheet which uses
        # styles created above.
        masterSheet = Master(MASTER_LIST_SHEET_NAME)
        resultsSheet = Results(RESULT_LIST_SHEET_NAME)
        inputSheet = Inputs(INPUT_LIST_SHEET_NAME)
        conditionalFormat.createDetailsConditionalFormats(unoDetailsSheet, masterSheet, resultsSheet, inputSheet, viewName)
        # Set new sheet as currently active sheet.
        helper.setActiveSheet(unoDetailsSheet)
    except errors.MovelisterError as e:
        helper.setActiveSheet(e.activeSheet)
        message_box.showWarningWithOk(str(e))


def updateOverviewFromActiveSheet(*args):
    """
    This function is used in the Overview-template buttons. It checks if
    Overview is attempted to update from an Overview instead of Master List and
    gives the relevant Overview-name from sheet instead of Master List in that
    case.
    """
    active = helper.getActiveSheetName()

    if active != 'Master List':
        updateOverview(activeSheet=active)
    else:
        updateOverview()


def updateOverview(*args, **kwargs):
    """
    A macro function to update or create a new Overview sheet. Updated sheet
    will include earlier user data in the old Overview if any.
    """
    try:
        if not Sheet.checkTemplatesExists():
            message_box.showWarningWithOk('This file doesn\'t seem to have all necessary templates. Can\'t generate.')
            return

        # Get name of the Overview which user wants to generate.
        masterSheet = Master(MASTER_LIST_SHEET_NAME)
        activeSheetName = kwargs.get('activeSheet', '')
        if activeSheetName == '':
            viewName = masterSheet.getOverviewName()
            overviewSheetName = names.getOverviewName(viewName)
        else:
            viewName = names.getViewName(activeSheetName)
            overviewSheetName = activeSheetName

        # Some error checking.
        if not viewName:
            message_box.showWarningWithOk('You can\'t generate an Overview if no View-name is set in cell C1.')
            return

        if viewName not in masterSheet.getViewNames():
            message_box.showWarningWithOk('You can\'t generate a View that has no Actions. Make sure at least one ' +
                                          'Action uses the View-name written in cell C1 before continuing.')
            return

        oldOverview = Overview(viewName)
        # If document has existing Overview, then that is set as previous instead.
        if Sheet.hasByName(overviewSheetName):
            # Check if user wants to update existing Overview.
            if not message_box.showSheetUpdateWarning():
                return
            oldOverview = Overview.fromSheet(overviewSheetName)

        newOverview = UpdateOverview.update(oldOverview, viewName)

        # Place new Overview sheet on the same position as the previous one. If previous one
        # does not exist, then place right of the Master sheet instead.
        position = Sheet.getPosition(overviewSheetName)
        if not position:
            position = Sheet.getPosition(MASTER_LIST_SHEET_NAME) + 1
        # Delete old sheet if exists.
        Sheet.deleteSheetByName(overviewSheetName)
        # Generate a new one.
        formatter = OverviewFormatter(newOverview)
        unoOverviewSheet = formatter.generate(position)
        # Make columns width optimal.
        length = cursor.getWidth(unoOverviewSheet)
        format.setOptimalWidthToRange(unoOverviewSheet, 0, length)
        # Fix sheet colors.
        formatter.setOverviewModifierColors(overviewSheetName)
        # Set new sheet as currently active sheet.
        helper.setActiveSheet(unoOverviewSheet)
    except errors.MovelisterError as e:
        helper.setActiveSheet(e.activeSheet)
        message_box.showWarningWithOk(str(e))

def showCurrentVersion(*args):
    """
    A macro function used in the About-sheet. Shows current version
    alongside other data about Movelister.
    """
    ver = version.getCurrentVersion()
    credits = 'Kazhuu and Nelitarnia'
    link = 'https://github.com/Kazhuu/movelister'
    message = ('Movelister v{0} \n \n'
           'Made by {1} \n \n'
           'Movelister is licensed under the MIT License. \n\n'
           'Home page of the project: \n'
           '{2}'
    ).format(ver, credits, link)
    message_box.createMessage('OK', 'Version information:', message)


# Run this when executed from the command line.
if __name__ == '__main__':
    Context.setup(host='localhost', port=2002)
    # showCurrentVersion()
    updateDetails(activeSheet='Overview (Default)')
    # updateOverview()
