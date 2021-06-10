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

	def analyze(self, text, candidate_post=['NOUN', 'PROPN', 'VERB'],
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
# text = '\n          \nCardano Foundation announces its delegation methodology - CLOSED\n\nZUG, 7 OCTOBER 2020. The Cardano Foundation is pleased to share its delegation methodology in accordance with our transparency principles, and in line with our promise to communicate to the wider community during each part of the delegation process.\nAs an independent Swiss foundation, it is the Cardano Foundation’s job to ensure that the Cardano blockchain achieves sufficient decentralization, to increase stake pool operator engagement and empower individual stake pools, and to support the staking and delegation infrastructure delivered through Shelley.\nSince the delivery of Shelley, the Cardano blockchain and its ecosystem partners have achieved more than 1,300 active stake pools, operated and maintained by dedicated and talented individual stake pool operators (SPOs)—who collectively, have enabled over 50% of the total ada (₳) circulating supply to be staked.\nThis tremendous feat has made Cardano one of the most decentralized blockchains to date in an incredibly short space of time, and it is a true testament to the strength and participation of our valued community. It is also indicative of the wealth of technical talent we have within our community—particularly promising ahead of the launch of native tokens, smart contracts, and decentralized applications.\nThe Cardano Foundation has supported the community with various initiatives, such as the Stake Pool School, a resounding success with over 3,000 participants successfully completing the course.\nIn the spirit of transparency in which the Cardano Foundation was founded, we are now pleased to publicly share our delegation methodology. Our delegation preferences and methodology has been carefully designed to support the ongoing decentralization of the Shelley mainnet, by supporting and involving new individual stake pools.\nWe will support stake pools of all sizes and regularly engage in a dialogue with our SPO community through our Community Management team. Our methodology will further evolve and develop over time.\n\nThe Cardano Foundation’s delegation methodology\nFor stake pools to be eligible for delegation from the Cardano Foundation, they must fall within the following criteria (data sourced from a self-hosted passive node):\n\nHold between ₳25,000 and ₳2mn as a pledge,\nOperated by a stakepool operator that only runs one pool (difficult to verify but best effort attempt),\nHave a normal operating cost of less than 5% variable rate, and a fixed rate of around ₳340,\nDoes not have a high number of ada already staked (less than 5% saturation),\nHave validated blocks successfully in the past,\nHave not been delegated to by the Cardano Foundation in the last four rounds.\n\nTo randomly select stake pools to delegate to, the Cardano Foundation will use a third party randomizer to choose from eligible pools according to the criteria listed above. As and when Daedalus implements non-myopic rankings, we shall implement this approach to stake pool selection.\nGoing forward re-delegation shall occur approximately every three epochs. Should an epoch end on a weekend, re-delegation shall be completed the following week.\nIn total, the Cardano Foundation has multiple wallets from which we will delegate our ada assets. Our ada assets are equally distributed across our wallets. Single wallets will be used to delegate to one pool at a time.\nThe first 10 stake pools the Cardano Foundation re-delegated to are, in alphabetical order:\n\nADAU,\nAGIO,\nAZTEC,\nBEAVR,\nCASP,\nCOSD,\nLOOT,\nWAAUS,\nZETIC,\nZONE.\n\nAs we test and gain access to more secure custody solutions, we shall add more wallet addresses and delegate our stake to a wider number of stake pools. We will be communicating our updated delegation preferences every three epochs.\n\nTogether, we can make Cardano more decentralized\nAs an ecosystem, we should be immensely proud of how much we have already achieved. Our official ‘Operating a Stake Pool’ Forum community, and the ‘Cardano Shelley & Stake Pool Best Practice’ Telegram group which has almost 4,300 users, are two of the busiest and most engaged segments of our community.\nHere and across other channels, we are delighted to see and participate in regular deep technical discussions, and gather welcome feedback from our stake pool operators.\nHowever, we are always looking to improve. We want to understand how we can attract more stake pool operators, simplify and enhance the onboarding journey, and make the operation of stake pools more attractive to a wider audience.\nIf you have suggestions and feedback on how this process could be enhanced, join the discussions on our Forum, and help us build a solid foundation for decentralization on Cardano, and contact our Community Management team.\nLikewise, we encourage each and every Cardano ecosystem participant with the skills and desire to become a stake pool operator to read our guide to becoming a stake pool operator, and sign up to the stake pool school.\n\nLearn more about staking, delegation, and consensus on the Cardano blockchain in the following articles:\n\nStaking and delegating for beginners—A step-by-step guide \nBlockchains of today versus blockchains of tomorrow\nChoosing a stake pool and delegating your ada\nConsensus on Cardano vs. other blockchains\n\n        ',
# text_rank = TextRank4Keyword()
# text_rank.analyze(str(text), window_size=4, candidate_post=['NOUN', 'PROPN', 'VERB'], stopwords={'%'})
# print(text_rank.get_keywords(8))
#
# result  = {'Cardano': '7.579779284357594', 'stake': '7.107714575409198', 'delegation': '4.682311876211349', 'pool': '4.517409368567867', 'Foundation': '3.970391667725273', 'pools': '3.521847399898127', 'community': '3.473617828556916', '%': '1.903930892583416', 'ada': '1.8977598117821746', 'Pool': '1.884235085608546'}
# result_ = {'Cardano': '7.605751506579816', 'stake': '7.136047908742533', 'delegation': '4.682311876211349', 'pool': '4.557469553753052', 'Foundation': '3.9763731492067547', 'pools': '3.529639066564794', 'community': '3.473617828556916', 'ada': '2.0070207807812372', 'Pool': '1.884235085608546', 'delegate': '1.8434009076420583'}
