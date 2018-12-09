from .sheet import Sheet
from movelister.core import cursor
from movelister.model import Modifier


HEADER_ROW = 0
DATA_BEGIN_ROW = 1

NAME_COLUMN = 0
COLOR_COLUMN = 2


class Modifiers:

    def __init__(self, sheetName):
        self.name = sheetName
        self.sheet = Sheet.getByName(sheetName)
        self.data = cursor.getSheetContent(self.sheet)
        self.dataHeader = self.data[HEADER_ROW]
        self.dataRows = self.data[DATA_BEGIN_ROW:]
        self.modifierColors = self._getModifierColors()

    def getModifiers(self):
        modifiers = []
        for index, row in enumerate(self.dataRows):
            if self._isValidRow(row):
                modifiers.append(Modifier(**self._modifierKwargs(row, index)))
        return modifiers

    def _isValidRow(self, row):
        return row[NAME_COLUMN] != ''

    def _modifierKwargs(self, row, index):
        kwargs = {'name': row[NAME_COLUMN]}
        kwargs['color'] = self.modifierColors[index]
        return kwargs

    def _getModifierColors(self):
        colors = []
        colorRange = self.sheet.getCellRangeByPosition(COLOR_COLUMN, DATA_BEGIN_ROW, COLOR_COLUMN, len(self.data))
        for index, row in enumerate(self.dataRows):
            colors.append(colorRange.getCellByPosition(0, index).CellBackColor)
        return colors