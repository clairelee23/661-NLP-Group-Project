# Preprocessor for the question generation 
# The preprocessor extracts sentences from .txt wikipedia articles, remove any noises, and tokenize sentences into words. 
import nltk
from nltk import word_tokenize, sent_tokenize,pos_tag
import os
import sys
from nltk.parse import stanford
from nltk.parse.stanford import StanfordParser
from nltk.parse.stanford import StanfordDependencyParser
from nltk.parse.stanford import StanfordNeuralDependencyParser
from nltk.tag.stanford import StanfordPOSTagger, StanfordNERTagger
from nltk.tokenize.stanford import StanfordTokenizer
from nltk.stem import WordNetLemmatizer
import string
import csv
from difflib import SequenceMatcher

lemmatizer = WordNetLemmatizer()



#	Calculate the jaccard distance between two strings
#	a and b should be a list of tokens in the string
def jaccard_similarity(a,b):
	a = set(a)
	b = set(b)
	c = a.intersection(b)
	return float(len(c)) / (len(a) + len(b) - len(c))

#	A Jaccard based similarity measure
def similarity(sent,question_content, percentage):
	#score = len(set(sent).intersection(set(question_content)))
	a = set(sent)
	b = set(question_content)
	c = a.intersection(b)
	score = float(len(c)) / (len(a) + len(b) - len(c))
	#	The sentence needs to contain all words in the question content, if not, return 0
	#print(sent)
	for q_word in question_content:
		#fuzzy matching
		found = False
		for s_word in sent:
			percentage_similarity = SequenceMatcher(None, q_word, s_word).ratio()
			if percentage_similarity >= percentage:
				found = True
		if not found:
			score -= 1
			#print(q_word)
	#print
	return	score 


#	Customized similarity measure for why type of question
def similarity_why(sent,question_content):
	a = set(sent)
	b = set(question_content)
	c = a.intersection(b)
	score = float(len(c)) / (len(a) + len(b) - len(c))
	
	found = False
	for q_word in ['because','for','since']:
		if q_word not in sent:
			pass
		else:
			found = True
	if not found:
		score = 0
		
	return	score 

#	Intersection between two lists
def intersection(lst1, lst2):
	lst3 = [value for value in lst1 if value in lst2]
	return lst3


# cur: currect tree
# label: target label
# record: candidates
def searchLabel(cur, label, record):
	answer = None
	if cur.label() == label:
		# record.append(cur.leaves())
		record.append(cur)
	for i in cur:
		# print "--",    (i), isinstance(i, (str, unicode)), i
		if not isinstance(i, (str, unicode)) and i.label() == label:
			# record.append(i.leaves())
			record.append(i)
		else:
			if len(i):
				if isinstance(i[0], (str, unicode)):
					continue
				else:
					for j in i:
						searchLabel(j, label, record)

def main():
	# stanford_pos_dir = '/Users/yuyanzhang/Desktop/CMU/NLP/project/tools/stanford-postagger-full-2015-04-20/'
	# eng_model_filename= stanford_pos_dir + 'models/english-bidirectional-distsim.tagger'
	# my_path_to_jar= stanford_pos_dir + 'stanford-postagger.jar'
	# st = StanfordPOSTagger(model_filename=eng_model_filename, path_to_jar=my_path_to_jar) 
	# print(st.tag('What is the airspeed of an unladen swallow ?'.split()))


	# # NER Tagging:
	stanford_ner = '/Users/yuyanzhang/Desktop/CMU/NLP/project/tools/stanford-ner-2015-04-20/'
	# stanford_ner_model = stanford_ner + 'classifiers/english.all.3class.distsim.crf.ser.gz'
	stanford_ner_model = stanford_ner + 'classifiers/english.muc.7class.distsim.crf.ser.gz'
	stanford_ner_jar = stanford_ner + 'stanford-ner.jar'
	ner = StanfordNERTagger(model_filename=stanford_ner_model, path_to_jar=stanford_ner_jar)
	#print(ner.tag('Rami Eid is studying at Stony Brook University in NY'.split()))

	# Set up the stanford PCFG parser
	stanford_parser_dir = '/Users/yuyanzhang/Desktop/CMU/NLP/project/tools/stanford-parser-full-2015-04-20/'
	eng_model_path = stanford_parser_dir  + "stanford-parser-3.5.2-models/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"
	my_path_to_models_jar = stanford_parser_dir  + "stanford-parser-3.5.2-models.jar"
	my_path_to_jar = stanford_parser_dir  + "stanford-parser.jar"
	parser=StanfordParser(model_path=eng_model_path, path_to_models_jar=my_path_to_models_jar, path_to_jar=my_path_to_jar)
	# sent = "Seth Kramer, one of the directors, describes how he first got the idea for The Linguists when in Vilnius, Lithuania, he could not read Yiddish inscriptions on a path in spite of his Jewish heritage."
	# parser_result =(parser.parse("The random person on the street eats meat.".split()))
	# for a in parser_result:
	# 	getNodes(a)
	# 	print("\u")
	# 	
	

	#	Read in the article and list of questions
	article_path = sys.argv[1]
	question_list = sys.argv[2]

	#	Tokenize all sentences
	sentences_pool = []

	article = open(article_path).read()
	paragraphs = [p for p in article.split('\n') if p]
	for paragraph in paragraphs[1:len(paragraphs)]: #	Skip the title
		# sentences = sent_tokenize(paragraph)
		sentences = sent_tokenize(paragraph.decode('utf-8'))
		for sentence in sentences:
			sentence_tokenized = [a.lower() for a in word_tokenize(sentence)]
			sentences_pool.append(sentence_tokenized)
			
	#	Answer questions in the quesiton list
	count = 0

	#	Read in the lemmatized the sentences
	# sentences_pool_lemmatized = []

	# Uncomment if the lemmatized sentence pool hasn't been generated yet
	# This step takes a long time, so you only need to run lemmatizaiton onece and you can load
	# the lemmatized setences from file to try different things after 
	# with open('sentences_pool_lemmatized.csv','w') as f:
	# 	writer = csv.writer(f,delimiter="\t")
	# 	for sent in sentence_pool:
	# 		sent = [a for a in sent if a != '\t']
	# 		sentences_lemmatized = [lemmatizer.lemmatize(i,j[0].lower()) if j[0].lower() in ['a','n','v'] else lemmatizer.lemmatize(i) for i,j in pos_tag(sent)]
	# 		sentences_pool_lemmatized.append(sentences_lemmatized)
	# 		writer.writerow(sentences_lemmatized)
	
	# with open('sentences_pool_lemmatized.csv') as f:
	# 	for line in f:
	# 		line = [a.lower() for a in line.strip().split("\t")]
	# 		sentences_pool_lemmatized.append(line)

	with open(question_list) as f:
		#	For each question on the list
		for question in f:
			count += 1
			question_tokenized = word_tokenize(question)
			question_tokenized_lower = [a.lower() for a in question_tokenized]
			question_start = question_tokenized_lower[0]

			
			# # Control the type of question 
			# if question_start in ['when','where']:
			# 	pass
			# else:
			# 	continue 
			
			#	Seperate question words and question content
			#  filtered_list = [a for a in string.punctuation]
			
			filtered_list = ['?','when', 'what','where','what','why','which','who','how','do','does','did','a','the','an']
			question_content = [a for a in question_tokenized_lower if a not in filtered_list]

			#	Lemmatize the question
			#question_lemmatized = [lemmatizer.lemmatize(i,j[0].lower()) if j[0].lower() in ['a','n','v'] else lemmatizer.lemmatize(i) for i,j in pos_tag(question_content)]
			
			
			#	Find the most similar sentences in the pool 
			max_similarity = None
			most_similar_sent = [] #	We need to consider ties

			for sent_idx in range(len(sentences_pool)):
				sent = sentences_pool[sent_idx]
				
				#similarity_score = jaccard_similarity(sent,question_content)+similarity(sent,question_content)
				if question_start == 'why':
					similarity_score = similarity_why(sent,question_content)
				else:
					similarity_score = similarity(sent,question_content, 0.8)
				
				if max_similarity == None:
					max_similarity = similarity_score
					#	Append the origin un-lemmatized sentence
					most_similar_sent.append(sentences_pool[sent_idx])
				elif similarity_score > max_similarity:
					max_similarity = similarity_score
					most_similar_sent.append(sentences_pool[sent_idx])
				else:
					pass
			

			# print((most_similar_sent))
			# print

			#	Now, build the answer from the retrieved sentence
			same_word = set(most_similar_sent[0])
			for s in most_similar_sent[1:]:
				same_word.intersection_update(s)
			
			#	Find the most relevant sentence
			max_similarity_2 = None
			max_similar_sent = None

			for sent in most_similar_sent:
				sent_filtered = [a for a in sent if not a in same_word]
				similarity_socre_2 = similarity(sent_filtered,question_content, 1)
				if max_similarity_2 == None:
					max_similarity_2 = similarity_socre_2
					max_similar_sent = sent
				elif similarity_socre_2 > max_similarity_2:
					max_similarity_2 = similarity_socre_2
					max_similar_sent = sent
			# print(max_similar_sent)
			#	Build answer based on different type of question
			answer = "NULL"
			try:
				#	Yes/No question: answer should contain only yes or no.	
				if question_start in ["is","was","are","were","do","does","did","have","has","had", "wasn't","isn't","aren't"]:
					#	First, convert sentence into a declarative sentence
					if max_similarity_2 == 0:
						answer = "No"
					else:
						question_parse = parser.parse(question_tokenized)
						for parse in question_parse:
							# print(parse)
							verb = parse[0][0].leaves()
							sub = (parse[0][1].leaves())
							obj = (parse[0][2].leaves())
							#substring = " ".join((sub+verb+obj))
							# If yes, most of the words in objects should be in the original sentence
							obj = [a.lower() for a in obj]
							if float(len(intersection(obj,max_similar_sent))) / len(obj)  >= 0.8:
								answer = "Yes"
							else:
								answer = "No"
							
						#	TODO: parse candidate sentence
						# answer = "No"
						# similar_sent_parse = parser.parse(max_similar_sent)
						# for parse in similar_sent_parse:
						# 	verb_ = parse[0][0].leaves()
						# 	sub_ = (parse[0][2].leaves())
						# 	obj_ = (parse[0][1].leaves())
						
				elif question_start == 'why':
					max_similar_sent_str = " ".join(max_similar_sent)
					reason_idx = max_similar_sent_str.index('because of')
					answer = max_similar_sent_str[len('because of'):len(max_similar_sent_str)]
					if reason_idx == -1:
						reason_idx = max_similar_sent_str.index('because')
						answer = max_similar_sent_str[len('because'):len(max_similar_sent_str)]
					if reason_idx == -1:
						reason_idx = max_similar_sent_str.index('for')
						answer = max_similar_sent_str[len('for'):len(max_similar_sent_str)]
					if reason_idx == -1:
						answer = "NULL"


				elif question_start == 'when':
					# 1. Tag: 'DATE', 'TIME'
					# 2.1. one PP or one CD in PP, return it
					# 2.2. multi candidate, return max_similar_sent
					found_DATE = False
					max_similar_sent_tag = ner.tag(max_similar_sent)
					# print max_similar_sent_tag 
					# Uncomment for dry run
					for pair in max_similar_sent_tag:
						if pair[1] == 'DATE' or pair[1] == 'TIME':
							answer = pair[0]
							found_DATE = True
					if not found_DATE:
						#TODO: deal with this situation
						max_similar_parse = parser.parse(max_similar_sent)
						for mparse in max_similar_parse:
							#print mparse
							stack = mparse
							answer = max_similar_parse
							record1 = []                            
							record2 = []
							for i in stack:
								searchLabel(i, "PP", record1)
								# print "-------", record1
							if len(record1) == 1:
								answer = record1[0].leaves()     
							else:
								for j in record1:
									searchLabel(j, "CD", record2)
								if len(record2) == 1:
									answer = record2[0].leaves()

				elif question_start == 'who':
					max_similar_sent_tag = ner.tag(max_similar_sent)
					found_PERSON = False
					for pair in max_similar_sent_tag:
						if pair[1] == 'PERSON':
							answer = pair[0]
							found_PERSON = True
					if not found_PERSON:
						#TODO: deal with this situation
						pass

				elif question_start == 'where':
					found_LOCATION = False
					max_similar_sent_tag = ner.tag(max_similar_sent)
					for pair in max_similar_sent_tag:
						if pair[1] == 'LOCATION' or pair[1] == 'LOCATION':
							answer = pair[0]
							found_LOCATION = True
					if not found_LOCATION:
						max_similar_parse = parser.parse(max_similar_sent)
						for mparse in max_similar_parse:
							#print mparse
							stack = mparse
							answer = max_similar_sent
							record1 = []
							record2 = []
							for i in stack:
								searchLabel(i, "PP", record1)
								# print "-------", record1
							if len(record1) == 1:
								if record1[0][0][0] in ("in", "from", "at", "on", "under"):
									answer = record1[0].leaves()     
							else:
								for j in record1:
									searchLabel(j, "CD", record2)
								if len(record2) == 1:
									answer = record2[0].leaves()

				elif question_start == 'how':
					question_second = question_tokenized_lower[1]
					temp = ['old', 'long', 'many', 'much', 'tall', 'heavy']
					max_similar_sent_str = " ".join(max_similar_sent)
					if question_second not in temp:
					  answer = max_similar_sent_str
					else:
					  number = [int(s) for s in max_similar_sent_str.split() if s.isdigit()]
					  tagged = pos_tag(max_similar_sent)
					  token_candidates = []
					  for token, label in tagged:
						splited = token.split('-')
						if len(splited) > 1:
						  for t in splited:
							if t.isdigit():
							  token_candidates.append(t)
						if label == 'CD':
						  token_candidates.append(token)
					  if len(token_candidates) > 1:
						answer = max_similar_sent_str
					  elif len(token_candidates) == 1:
						answer = token_candidates[0] 
					  else:
						answer = "NULL" 
					
				#For what, which,and others
				else:
					#print(count,question)
					try:
						question_parse = parser.parse(question_tokenized)
						for parse in question_parse:
							#print(parse)
							verb = parse[0][1].leaves()
							sub = (parse[0][1][1].leaves())
							#obj = (parse[0][2].leaves())
							#print(verb,sub)

						similar_sent_parse = parser.parse(max_similar_sent)
						for parse in similar_sent_parse:
							# print(parse)
							answer = parse[0][1][1].leaves()				
					except:
						pass
						#TODO: deal with this situation


				#Capitalize first letter

				if not answer:
					answer = "NULL"
				elif question_start == 'how':
					answer = answer.capitalize()
				else:
					answer = " ".join(answer)

					a = list(answer)
					if a:
						a[0] = a[0].upper()
						answer = "".join(a)
				print(' '.join(question_tokenized))
				print(answer)
			except:
				print(" ".join(max_similar_sent))

		

if __name__ == '__main__':
	main()
