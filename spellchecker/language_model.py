# language model for computing the probability of the query
# query = w_1 ... w_n (words)
# unigram model: P(query) = P(w_1, ..., w_n) = P(w_1) * ... * P(w_n)
# bigram model: P(w_1, w_2) = P(w_1|w_2) * P(w_2)
# P(query) = P(w_1, ..., w_n) = P(w_1|w_2) * P(w_2|w_3) * ... * P(w_n)

import numpy as np
import json
from collections import defaultdict
from utils import split


class LanguageModel:

    def __init__(self):

        # dictionary = {"word": probability_of_word}, contains P(w_i) for unigram model
        self.unigram_probabilities = defaultdict(float)

        # dictionary = {("first_w", "second_w") : conditional_probability_of_word},
        # contains P(w_1|w_2) for bigram model
        # P(w_1|w_2) = P(w_1, w_2) / P(w_2)
        self.bigram_probabilities = defaultdict(float)

        # number of all words (unigrams) in all queries
        self.unigram_number = 0

        # number of all pairs of words (bigrams) in all queries
        self.bigram_number = 0

        # probabilities for new words which are not in dictionary
        self.unigram_default_probability = 0
        self.bigram_default_probability = 0

    # computing unigram and bigram probabilities
    def fit(self, filename):

        with open(filename, "r") as file:
            for line in file:
                ind = line.find('\t')
                if ind != -1:
                    line = line[ind + 1:]  # count correct queries
                words = split(line)

                len_words = len(words)
                for i in range(len_words):
                    self.unigram_probabilities[words[i]] += 1
                    self.unigram_number += 1
                    if i < len_words - 1:
                        self.bigram_probabilities[(words[i], words[i + 1])] += 1
                        self.bigram_number += 1

        for i in self.unigram_probabilities:
            self.unigram_probabilities[i] /= self.unigram_number
        for i in self.bigram_probabilities:
            second_word = i[1]
            self.bigram_probabilities[i] /= self.bigram_number * self.unigram_probabilities[second_word]

        self.unigram_default_probability = 1 / self.unigram_number
        self.bigram_default_probability = 1 / self.bigram_number

    # compute probability of the query
    # P(query) = P(w_1, ..., w_n) = P(w_1|w_2) * P(w_2|w_3) * ... * P(w_n)
    def get_probability(self, query):
        words = split(query)
        len_words = len(words)
        if len_words < 2:
            return self.unigram_default_probability

        probabilities = np.zeros(len_words)
        for i in range(len_words):
            if i < len_words - 1:
                if (words[i], words[i + 1]) in self.bigram_probabilities:
                    probabilities[i] = self.bigram_probabilities[(words[i], words[i + 1])]
                else:
                    probabilities[i] = self.bigram_default_probability
            else:
                if words[i] in self.unigram_probabilities:
                    probabilities[i] = self.unigram_probabilities[words[i]]
                else:
                    probabilities[i] = self.unigram_default_probability
        return np.prod(probabilities)

    def to_json(self, filename1, filename2):
        with open(filename1, "w") as write_file:
            write_file.write(json.dumps((self.unigram_number, self.unigram_probabilities)))
        with open(filename2, "w") as write_file:
            write_file.write(json.dumps((self.bigram_number, self.bigram_probabilities)))

    def from_json(self, filename1, filename2):

        with open(filename1, "r") as read_file:
            (self.unigram_number, self.unigram_probabilities) = json.loads(read_file.read())
        with open(filename2, "r") as read_file:
            (self.bigram_number, self.bigram_probabilities) = json.loads(read_file.read())

        self.unigram_default_probability = 1 / self.unigram_number
        self.bigram_default_probability = 1 / self.bigram_number
