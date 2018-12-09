from com.sun.star.uno import RuntimeException

from test import OfficeTestCase
from movelister.core import Context
from movelister.sheet import Sheet


class SheetTestCase(OfficeTestCase):

    def testNewSheet(self):
        newName = 'test sheet'
        sheet = Sheet.newSheet(newName, 0)
        self.assertEqual(sheet.getName(), newName)

    def testNewSheetWithExistingName(self):
        with self.assertRaises(RuntimeException):
            Sheet.newSheet('Master List', 0)

    def testGetPosition(self):
        position = Sheet.getPosition('Modifier List')
        self.assertEqual(position, 4)

    def testGetWrongPosition(self):
        with self.assertRaises(ValueError):
            Sheet.getPosition('fails')

    def testGetSheetNames(self):
        names = Sheet.getSheetNames()
        for name in names:
            self.assertIsInstance(name, str)

    def testNewSheetRightOf(self):
        rightOfName = 'Master List'
        name = 'test sheet'
        sheet = Sheet.newSheetRightOf(rightOfName, name)
        self.assertEqual(sheet.getName(), name)
        names = Context.getDocument().Sheets.getElementNames()
        index = names.index(rightOfName)
        self.assertEqual(names.index(name), index + 1)

    def testNewSheetLeftOf(self):
        leftOfName = 'Modifier List'
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