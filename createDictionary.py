import codecs
import re


corpus_file = codecs.open('arushi.txt', encoding='utf-8')
dictionary = {}
for line in corpus_file:
	print line
	forms = {}
	main_word = ""
	for word in line.split():
	# word = re.sub('[.!,;\']', '', word)
		if ":" in word:
			word = re.sub('[\[\]]', '', word)
			splits = word.split(":")
			form = splits[0]
			meanings = splits[1]
			# print "------"
			# print form
			# print meanings
			forms[form] = meanings
		else:
			main_word = word
	dictionary[main_word] = forms
	

	print main_word
	#print forms
	

	for w in dictionary[main_word]:
		print 
		print 



    


corpus_file.close()

