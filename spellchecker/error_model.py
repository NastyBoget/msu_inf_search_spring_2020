# Bigram statistics

from collections import defaultdict
import numpy as np
import json
from nltk import ngrams
from utils import split, levenshtein_distance


class ErrorModel:

    def __init__(self, filename):

        # dictionary = {("right_bigram", "wrong_bigram") : probability_of_bigram}
        self.bigram_probabilities = defaultdict(float)

        self.bigram_number = 0

        self.bigram_default_probability = 0

        self.filename = filename

    def fit(self):

        with open(self.filename, "r") as file:
            for line in file:
                ind = line.find('\t')
                # it's correct query
                if ind != -1:
                    continue
                wrong = split(line[:ind])
                right = split(line[ind + 1:])
                if len(wrong) != len(right):  # join or split
                    continue
                for i in range(len(wrong)):
                    self.add_bigrams(right[i], wrong[i])

        self.bigram_default_probability = 1 / self.bigram_number
        self.bigram_number = len(self.bigram_probabilities)
        for i in self.bigram_probabilities:
            self.bigram_probabilities[i] /= self.bigram_number

    def add_bigrams(self, right, wrong):

        # add special characters for indicating the beginning and the end of the word
        # use double characters for separating bigrams
        wrong = "".join(list(map(lambda z: "".join(z), ngrams('^' + wrong + '_', 2))))
        right = "".join(list(map(lambda z: "".join(z), ngrams('^' + right + '_', 2))))
        # levenshtein matrix for two words of the query
        # first word is horizontal, second - vertical
        matrix = levenshtein_distance(right, wrong, result='matrix')

        # compute path in matrix for fixing the word
        # begin from lower right corner of the matrix
        # if next position is above current -> delete character (0)
        # if next position is from the left -> add character (1)
        # if the next position is diagonally -> replace character (2)
        x, y = len(wrong), len(right)
        while x not in [0, 1] and y not in [0, 1]:
            right_bigram, wrong_bigram = np.array((2, 0), dtype=str), np.array((2, 0), dtype=str)
            for i in range(1, -1, -1):  # we have even amount of characters
                paths = np.array([matrix[x - 1, y], matrix[x, y - 1], matrix[x - 1, y - 1]])
                # states: 0, 1, 2
                next_pos = np.argmin(paths)
                if matrix[x, y] == paths[next_pos]:  # there is no error
                    right_bigram[i] = right[y - 1]
                    wrong_bigram[i] = wrong[x - 1]
                    if next_pos == 0:
                        x -= 1
                    elif next_pos == 1:
                        y -= 1
                    elif next_pos == 2:
                        x -= 1
                        y -= 1
                    continue
                # '~' means empty character
                # delete
                if next_pos == 0:
                    right_bigram[i] = '~'
                    wrong_bigram[i] = wrong[x - 1]
                    x -= 1
                # add
                elif next_pos == 1:
                    right_bigram[i] = right[y - 1]
                    wrong_bigram[i] = '~'
                    y -= 1
                # change
                elif next_pos == 2:
                    right_bigram[i] = right[y - 1]
                    wrong_bigram[i] = wrong[x - 1]
                    x -= 1
                    y -= 1
            # for accurate separating bigrams
            if x % 2 != 0:
                x -= 1
            if y % 2 != 0:
                y -= 1
            right_bigram = right_bigram[0] + right_bigram[1]
            wrong_bigram = wrong_bigram[0] + wrong_bigram[1]
            self.bigram_probabilities[(right_bigram, wrong_bigram)] += 1

    def to_json(self, filename):
        with open(filename, "w") as write_file:
            json.dump(self.bigram_probabilities, write_file)

    def from_json(self, filename):
        with open(filename, "r") as read_file:
            self.bigram_probabilities = json.load(read_file)
        self.bigram_number = len(self.bigram_probabilities)
        self.bigram_default_probability = 1 / self.bigram_number
