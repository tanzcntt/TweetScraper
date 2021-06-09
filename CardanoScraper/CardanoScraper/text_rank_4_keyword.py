import numpy as np
import spacy
from collections import OrderedDict
from spacy.lang.en.stop_words import STOP_WORDS

nlp = spacy.load('en_core_web_sm')
# en_core_web_sm is Available trained pipelines for English

# ================================================
# Target: get the POS tag of words
# ================================================
# POS tag is a process to mark up the words in text format for a particular paragraph
# depended on its Context and Definition
# define:
# PROPN: proper noun: Van, Tan Nguyen,...
# NOUN: noun: a desk, a pen
# concept:
# for the first one, we load text and store all word defined by each candidate_pos: NOUN, PROPN, ADJ,... into tuple
# after that calculate the weight for each node (word) by: words in each candidate_pos
# ex: defined words in NOUN: [w1, w2, w3, w4,..., wn]; [w1, w2, ..., w_k], [w2, w3, ..., w_{k+1}], [w3, w4, ..., w_{k+2}] are windows
# if we set window_size = 3, NOUN: [time, Wandering, Earth, feels, throwback], we get 3 windows [time, Wandering, Earth], [Wandering, Earth, feels], [Earth, feels, throwback]
# each window any two words pair has an undirected edge: (time, Wandering), (time, Earth), (Wandering, Earth).
# depended on this graph to calculate weight for each word and identify the most important words.


# install:
# english trained pipeline model: python -m spacy download en_core_web_sm

class TextRank4Keyword:
	"""Extract keyword from text"""

	def __init__(self):
		self.d = .85  # damping coefficient, usually is .85
		self.min_diff = 1e-5  # convergence threshold
		self.steps = 10  # iteration step
		self.node_weight = None  # save keyword and it weights

	def set_stopwords(self, stopwords):
		"""Set stop words"""
		for word in STOP_WORDS.union(set(stopwords)):
			lexeme = nlp.vocab[word]
			lexeme.is_stop = True

	def sentences_segment(self, doc, candidate_pos, lower):
		"""Store those words follow candidate_pos"""
		sentences = []
		for sent in doc.sents:
			selected_words = []
			for token in sent:
				# Store words only with candidate POS tag
				if token.pos_ in candidate_pos and token.is_stop is False:
					if lower is True:
						selected_words.append(token.text.lower())
					else:
						selected_words.append(token.text)
			sentences.append(selected_words)
		return sentences

	def get_vocab(self, sentences):
		"""Get all tokens"""
		vocab = OrderedDict()
		i = 0
		for sentence in sentences:
			for word in sentence:
				if word not in vocab:
					vocab[word] = i
					i += 1

		return vocab

	def get_token_pairs(self, window_size, sentences):
		"""Build token_pairs from windows in sentences"""
		token_pairs = list()
		for sentence in sentences:
			for index, word in enumerate(sentence):  # enumerate: simplify loop with counter and value
				for j in range(index + 1, index + window_size):
					if j >= len(sentence):
						break
					pair = (word, sentence[j])
					if pair not in token_pairs:
						token_pairs.append(pair)
		return token_pairs

	def symmetrize(self, a):
		return a + a.T - np.diag(a.diagonal())

	def get_matrix(self, vocab, token_pairs):
		"""Get normalized matrix"""
		vocab_size = len(vocab)
		g = np.zeros((vocab_size, vocab_size), dtype='float')
		for word1, word2 in token_pairs:
			i, j = vocab[word1], vocab[word2]
			g[i][j] = 1

		# get symmetric matrix
		g = self.symmetrize(g)

		# normalize matrix by column
		norm = np.sum(g, axis=0)
		g_norm = np.divide(g, norm, where=norm != 0)  # this is ignore the 0 element in norm

		return g_norm

	def get_keywords(self, number=10):
		"""print top number of this keyword"""
		node_weight = OrderedDict(sorted(self.node_weight.items(), key=lambda t: t[1], reverse=True))
		data = {}
		for i, (key, value) in enumerate(node_weight.items()):
			# print(key + ' - ' + str(value))
			data[key] = str(value)
			if i > number:
				break
		return data

	def analyze(self, text, candidate_post=['NOUN', 'PROPN', 'VERB', 'ADJ'],
				window_size=4, lower=False, stopwords=list()):
		# Set stop words
		self.set_stopwords(stopwords)
		# Parse text by spaCy
		doc = nlp(text)
		# Filter sentences
		sentences = self.sentences_segment(doc, candidate_post, lower)  # list: list of word
		# Build vocabulary
		vocab = self.get_vocab(sentences)
		# Get token_pairs from windows
		token_pairs = self.get_token_pairs(window_size, sentences)
		# Get normalized matrix
		g = self.get_matrix(vocab, token_pairs)
		# Initionlization for weight ()
		pr = np.array([1] * len(vocab))

		# Iteration
		previous_pr = 0
		for epoch in range(self.steps):
			pr = (1-self.d) + self.d * np.dot(g, pr)
			if abs(previous_pr - sum(pr)) < self.min_diff:
				break
			else:
				previous_pr = sum(pr)
		# Get weight for each node
		node_weight = dict()
		for word, index in vocab.items():
			node_weight[word] = pr[index]
		self.node_weight = node_weight


# with open('Data/half_a_billion_dollar.txt', 'r') as file:
# 	text = file.read()
#
# text_rank = TextRank4Keyword()
# text_rank.analyze(text, window_size=4)
# print(text_rank.get_keywords(8))
