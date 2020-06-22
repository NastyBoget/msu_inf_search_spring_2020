# language model for computing the probability of the query
# query = w_1 ... w_n (words)
# unigram model: P(query) = P(w_1, ..., w_n) = P(w_1) * ... * P(w_n)
# bigram model: P(w_1, w_2) = P(w_1|w_2) * P(w_2)
# P(query) = P(w_1, ..., w_n) = P(w_1|w_2) * P(w_2|w_3) * ... * P(w_n)

import numpy as np
from collections import defaultdict
from utils import split
import pickle as pkl


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
        print('language model is fitting')
        line_num = 0
        with open(filename, "r") as file:
            for line in file:
                line_num += 1
                if line_num > 100000:
                    break
                print(f"\r{line_num} lines are processed...", end='', flush=True)
                ind = line.find('\t')
                if ind != -1:
                    line = line[ind + 1:]  # count incorrect queries
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
    def get_probability(self, query, unigram=False, smooth=1):
        words = split(query)
        len_words = len(words)

        probabilities = np.zeros(len_words)
        if unigram:
            for i in range(len_words):
                if words[i] in self.unigram_probabilities:
                    probabilities[i] = self.unigram_probabilities[words[i]] ** smooth
                else:
                    probabilities[i] = self.unigram_default_probability ** smooth
        else:
            for i in range(len_words):
                if i < len_words - 1:
                    if (words[i], words[i + 1]) in self.bigram_probabilities:
                        probabilities[i] = self.bigram_probabilities[(words[i], words[i + 1])] ** smooth
                    else:
                        probabilities[i] = self.bigram_default_probability ** smooth
                else:
                    if words[i] in self.unigram_probabilities:
                        probabilities[i] = self.unigram_probabilities[words[i]] ** smooth
                    else:
                        probabilities[i] = self.unigram_default_probability ** smooth
        return np.prod(probabilities)

    def save_model(self, filename1, filename2):
        with open(filename1, "wb") as write_file1, open(filename2, "wb") as write_file2:
            pkl.dump((self.unigram_number, self.unigram_probabilities), write_file1, protocol=pkl.HIGHEST_PROTOCOL)
            pkl.dump((self.bigram_number, self.bigram_probabilities), write_file2, protocol=pkl.HIGHEST_PROTOCOL)

    def load_bigram(self, filename):
        with open(filename, "rb") as read_file:
            data = pkl.load(read_file)
            self.bigram_number, self.bigram_probabilities = data
        self.bigram_default_probability = 1 / self.bigram_number

    def load_unigram(self, filename):
        with open(filename, "rb") as read_file:
            data = pkl.load(read_file)
            self.unigram_number, self.unigram_probabilities = data
            self.unigram_default_probability = 1 / self.unigram_number
