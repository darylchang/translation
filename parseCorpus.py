import codecs
import re


corpus_file = codecs.open('corpus.txt', encoding='utf-8')
for line in corpus_file:
    print line
    for word in line.split():

    	word = re.sub('[.!,;\']', '', word)
    	print word

    	



corpus_file.close()
