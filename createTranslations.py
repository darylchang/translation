import re

def createTranslations():
	f = open('dictionary.txt', 'r').readlines()
	translationDict = {}
	for line in f:
		spaceIndex = line.find(' ')
		word = line[:spaceIndex] 
		translations = line[spaceIndex+1:]

		if not re.search('\[(.*?)\]', translations):
			# Takes care of proper nouns
			translationDict[word] = [('noun', word[:1].upper() + word[1:])] 
		else:
			# Parse translations
			posGroups = re.findall('\[(.*?)\]', translations)
			arr = []
			for posGroup in posGroups:
				pos, translationString = posGroup.split(':')
				translationSplit = translationString.split(',')
				for t in translationSplit:
					arr.append((pos, t))
			translationDict[word] = arr
	return translationDict