import copy

# Return whether or not the previous token in the sentence was removed
# as a stop word. This is true if:
#       1. Last element of list is True
#       2. Previous index of removable token is directly before this one
def prevTokenRemoved(removePositions, index, sublist):
    if not sublist[-1]:
        return False
    if index == 0 or removePositions[index-1] < (removePositions[index]-1):
        return False
    return False

def iterBools(lists, removePositions, index, remaining):
    if not lists and remaining > 0:
        lists = [[True], [False]]
        remaining -= 1
    if remaining <= 0:
        return lists
    newLists = []
    for sublist in lists:
        falseList = copy.deepcopy(sublist)
        falseList.append(False)
        newLists.append(falseList)

        if not prevTokenRemoved(removePositions, index, sublist):
            trueList = copy.deepcopy(sublist)
            trueList.append(True)
            newLists.append(trueList)
    return iterBools(newLists, removePositions, index + 1, remaining - 1)
