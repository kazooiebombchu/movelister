from movelister.context import Context


def getCurrentSelection():
    """
    This function just gets the current active Selection and returns it.
    """
    model = Context.getDocument()
    sel = model.getCurrentSelection()

    return sel


def determineSelectionType(selection):
    """
    This function figures out if the current selection is single or multiple.
    It then returns a string SINGLE or MULTI.
    """

    if selection is None:
        exit()

    if "ScCellObj" in str(selection):
        return('SINGLE')

    if "ScCellRangeObj" in str(selection):
        return('MULTI')
