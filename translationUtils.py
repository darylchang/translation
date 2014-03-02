import copy

def iterBools(lists, remaining):
    if not lists and remaining > 0:
        lists = [[True], [False]]
        remaining -= 1
    if remaining <= 0:
        return lists
    newLists = []
    for sublist in lists:
        trueList = copy.deepcopy(sublist)
        falseList = copy.deepcopy(sublist)
        trueList.append(True)
        falseList.append(False)
        newLists.extend([trueList, falseList])
    return iterBools(newLists, remaining - 1)
