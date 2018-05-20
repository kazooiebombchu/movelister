"""
Main file for the all usable LibreOffice macros. Can also be executed from the
command line and connect to opened LibreOffice socket.
"""

import os
import sys

# This is to emulate how LibreOffice adds pythonpath folder to PYTHONPATH where
# the script is executed. PYTHONPATH is added when executing from the command
# line.
if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname('__file__'), 'pythonpath'))

from movelister import environment, group, inputList, test  # nopep8


def kappa(**kwargs):
    model = environment.getDocument(**kwargs)
    model.Sheets.insertNewByName("Nojes", 0)
    newSheet = model.Sheets.getByName("Nojes")
    newSheet.getCellByPosition(0, 0).setString("Test")
    a = 1
    testCell = newSheet.getCellByPosition(1, 1)
    testCell.setString(a)


def printInputList(**kwargs):
    model = environment.getDocument(**kwargs)
    sheet = model.CurrentController.ActiveSheet
    inputSheet = model.Sheets.getByName("Input Lists")
    inputGroupName = "Default"
    inputsArray = [[0], [0], [0]]
    inputsArray = inputList.getInputList(inputSheet, inputGroupName)
    test.testItOut(inputSheet, inputsArray)


def groupRows(**kwargs):
    model = environment.getDocument(**kwargs)
    sheet = model.CurrentController.ActiveSheet
    startRow = 10
    endRow = 20
    group.groupRows(sheet, startRow, endRow)


# Tuple of exported functions seen by LibreOffice.
g_exportedScripts = (kappa, groupRows)

# Run when executed from the command line.
if __name__ == '__main__':
    printInputList(host='localhost', port=2002)
