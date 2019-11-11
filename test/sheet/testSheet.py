from com.sun.star.uno import RuntimeException

from test import OfficeTestCase
from movelister.core import Context
from movelister.sheet import Sheet, MASTER_LIST_SHEET_NAME, MODIFIER_LIST_SHEET_NAME


class SheetTestCase(OfficeTestCase):

    def testNewSheet(self):
        newName = 'test sheet'
        sheet = Sheet.newSheet(newName, 0)
        self.assertEqual(sheet.getName(), newName)

    def testNewSheetWithExistingName(self):
        with self.assertRaises(RuntimeException):
            Sheet.newSheet(MASTER_LIST_SHEET_NAME, 0)

    def testGetPosition(self):
        position = Sheet.getPosition(MODIFIER_LIST_SHEET_NAME)
        self.assertEqual(position, 4)

    def testGetWrongPosition(self):
        with self.assertRaises(ValueError):
            Sheet.getPosition('fails')

    def testGetSheetNames(self):
        names = Sheet.getSheetNames()
        for name in names:
            self.assertIsInstance(name, str)

    def testNewSheetRightOf(self):
        rightOfName = MASTER_LIST_SHEET_NAME
        name = 'test sheet'
        sheet = Sheet.newSheetRightOf(rightOfName, name)
        self.assertEqual(sheet.getName(), name)
        names = Context.getDocument().Sheets.getElementNames()
        index = names.index(rightOfName)
        self.assertEqual(names.index(name), index + 1)

    def testNewSheetLeftOf(self):
        leftOfName = MODIFIER_LIST_SHEET_NAME
        name = 'test sheet'
        sheet = Sheet.newSheetLeftOf(leftOfName, name)
        self.assertEqual(sheet.getName(), name)
        names = Context.getDocument().Sheets.getElementNames()
        index = names.index(leftOfName)
        self.assertEqual(names.index(name), index - 1)

    def testNewSheetRightOfWithWrongName(self):
        rightOfName = 'fail'
        with self.assertRaises(ValueError):
            Sheet.newSheetRightOf(rightOfName, 'will fail')

    def testNewOverview(self):
        name = 'test'
        overViewName = 'Overview ({0})'.format(name)
        sheet = Sheet.newOverview(name)
        self.assertEqual(sheet.Name, overViewName)
        self.assertTrue(overViewName in Sheet.getSheetNames())