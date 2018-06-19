import itertools

from movelister import loop, messageBox, modifierList, test


def getMasterList(masterSheet):
    endRow = -1
    modEndCol = loop.getColumnLocation(masterSheet, 'Full Name') - 1

    # The loop iterates through Master Action List to get its end row.
    # The loop breaks once there are two empty rows or x is over 1000.
    endRow = loop.getEndOfList(masterSheet)

    # The four attributes for CellRangeByPosition are: left, top, right, bottom.
    # The data array consists of ALL relevant data in the sheet, including modifiers.
    range = masterSheet.getCellRangeByPosition(0, 0, modEndCol, endRow + 1)

    masterDataArray = range.getDataArray()
    return masterDataArray


def getMasterListProjection(masterSheet, modifierSheet):
    MDA = getMasterList(masterSheet)
    nameCol = loop.getColumnLocation(masterSheet, 'Action Name')
    modStartCol = loop.getColumnLocation(masterSheet, 'DEF')
    modEndCol = loop.getColumnLocation(masterSheet, 'Full Name') - 1
    modAmount = modEndCol - modStartCol
    currentName = MDA[1][nameCol]
    currentActionRow = -1
    projection = [[], []]
    currentActionDEF = -1
    currentActionMods = [[], []]
    currentActionMods.clear()
    currentActionPrereqs = []
    prereqsString = ''

    # A bit of error checking.
    if len(MDA) <= 2 and MDA[1][nameCol] == '':
        messageBox.createMessage('OK', 'Warning:', 'Master Action List seems to be empty. Unable to generate.')
        exit()

    # Get an array of impossible variations (derived from Modifier rules) to compare with the action list later on.
    antiVariationSet = modifierList.getImpossibleVariations(modifierSheet)
    print('All impossible combinations: ' + str(antiVariationSet))

    # Loop through rows of Master Action List (represented as the multi-dimensional List MDA).
    x = 0
    while x < len(MDA) - 1:
        x = x + 1
        currentActionRow = currentActionRow + 1

        # currentActionMods has to be appended each row so that it has space for listing all the 'x'
        # per each row of the animation.
        currentActionMods.append([])

        # Loop for going through all modifier columns.
        if currentName == MDA[x][nameCol]:
            y = -1
            while y < modAmount:
                y = y + 1

                # If first column (DEF) has 'x', there needs to be a modifier-less default version of the action.
                if MDA[x][modStartCol + y] == 'x' and y == 0 and currentActionDEF < 1:
                    currentActionDEF = 1
                    print('There will be a DEF version of ' + currentName)

                # If a column has 'x' in any other circumstance...
                # Collect all the 'x' for each row in a multi-dimensional array currentActionMods.
                if MDA[x][modStartCol + y] == 'x' and y > 0:
                    currentActionMods[currentActionRow].append(y)

                # If a cell has 'P' (prerequisite), store it for now.
                if MDA[x][modStartCol + y] == 'P' and y > 0:
                    currentActionPrereqs.append(MDA[0][modStartCol + y])

        # If currentName doesn't match current row, update it. This signifies the start of a new action.
        if currentName != MDA[x][nameCol]:

            # Make a string out of currentActionPrereqs if needed.
            if len(currentActionPrereqs) > 0:
                prereqsString = makePrereqsString(currentActionPrereqs, prereqsString)

            # Process the currentActionMods list to figure out all the possible variations of the action.
            # The procession happens row by row because otherwise some variations will be missed.
            if len(currentActionMods) > 1:
                sortedList = processVariations(currentActionMods, antiVariationSet)

                if currentActionDEF == 1:
                    projection[0].append(currentName)
                    projection[1].append(prereqsString)

                if len(sortedList) > 0:
                    print('The final list of combinations from ' + currentName + ': ' + str(sortedList))

                    # Add all the variations of the current attack in the projection.
                    projection = fillProjection(MDA, sortedList, projection, currentName, prereqsString, modStartCol)

            # Update currentName with new action and re-initialize variables for next action.
            currentName = MDA[x][nameCol]
            print('Next attack is ' + currentName)
            currentActionRow = -1
            currentActionMods.clear()
            currentActionPrereqs = []
            prereqsString = ''
            currentActionDEF = -1
            x = x - 1

    # A quick test that prints out the contents of the projection.
    test.printProjectionTest(projection, masterSheet)


def processVariations(currentActionMods, antiVariationSet):

    # Get a set of all possible variations of a single action.
    variationSet = getPossibleVariations(currentActionMods)
    filteredSet = variationSet.copy()

    # Delete impossible combinations from the set based on modifier rules.
    for imp in antiVariationSet:
        for item in variationSet:
            if match(item, imp):
                filteredSet.discard(item)

    # Delete empty from the set.
    emptySet = {()}
    refinedSet = filteredSet - emptySet

    # Sort the data.
    sortedList = sorted(refinedSet)
    return sortedList


def getPossibleVariations(currentActionMods):
    z = -1
    tempMods1 = []
    tempMods2 = []

    # The loop unpacks all values from currentActionMods to tempMods2.
    # Then calculates and appends all combinations of those values to tempMods1.
    while z < len(currentActionMods) - 1:
        tempMods2.clear()
        z = z + 1
        xyz = -1
        while xyz < len(currentActionMods[z]) - 1:
            xyz = xyz + 1
            tempMods2.append(currentActionMods[z][xyz])
            if len(tempMods2) > 0:
                for L in range(0, len(tempMods2) + 1):
                    for subset in itertools.combinations(tempMods2, L):
                        tempMods1.append(subset)

    # Converts tempMods1 into a set to delete all duplicates.
    tempSet = set(tempMods1)
    return tempSet


def fillProjection(MDA, sortedList, projection, currentName, prereqsString, modStartCol):
    tempString = ''

    # Add all the variations of the current attack in the projection.
    for xx in sortedList:
        for xxy in xx:
            if tempString == '':
                tempString = tempString + MDA[0][modStartCol + xxy]
            else:
                tempString = tempString + ' + ' + MDA[0][modStartCol + xxy]

        projection[0].append(currentName)
        if prereqsString != '':
            projection[1].append(prereqsString + ' + ' + tempString)
        else:
            projection[1].append(tempString)
        tempString = ''

    return projection


def makePrereqsString(currentActionPrereqs, prereqsString):

    # Makes a string out of the content of currentActionPrereqs.
    prereqsSet = set(currentActionPrereqs)
    for ouh in prereqsSet:
        if prereqsString == '':
            prereqsString = ouh
        else:
            prereqsString = prereqsString + ' + ' + ouh

    return prereqsString


def getHighestPhaseNumber(masterSheet, listLength):
    x = -1
    phase = 0
    phaseCol = loop.getColumnLocation(masterSheet, 'Phase')

    # The loop iterates through the Phase column and finds the highest number in sequence.
    # Warning: loop cannot find high phase numbers that are out of sequence.
    # But something like that shouldn't happen in normal use, right?
    # Warning: the loop also doesn't check if the high phase numbers are actually in use,
    # (as indicated by the Modifiers columns) so it doesn't do everything it's supposed to yet.
    while x <= listLength:
        x = x + 1
        if masterSheet.getCellByPosition(phaseCol, x).getValue() == phase:
            phase = phase + 1
            x = -1

    return(phase)


def match(combination, match):
    return all(elem in combination for elem in match)


def fixModifiers(masterSheet, modifierDataArray):
    print("TO DO")
