# Bigram statistics for error model

from collections import defaultdict
import numpy as np
import pickle as pkl
from nltk import ngrams
from utils import split, levenshtein_distance


class ErrorModel:

    def __init__(self):

        # dictionary = {("wrong_bigram", "right_bigram") : probability_of_right_bigram_for_this_wrong_bigram}
        # probability_of_right_bigram = number_of_(right, wrong) / sum_of_all_fixes_for_this_wrong
        self.bigram_probabilities = defaultdict(float)

        self.unigram_probabilities = defaultdict(float)

        # sum of all fixes
        self.bigram_number = 0

        self.bigram_default_probability = 0

        self.unigram_number = 0

        self.unigram_default_probability = 0

    def fit(self, filename):
        print('error model is fitting')

        with open(filename, "r") as file:
            line_num = 0
            for line in file:
                line_num += 1
                if line_num > 100000:
                    break
                print(f"\r{line_num} lines are processed...", end='', flush=True)
                ind = line.find('\t')
                # it's correct query
                if ind == -1:
                    continue
                wrong = split(line[:ind])
                right = split(line[ind + 1:])
                if len(wrong) != len(right):  # join or split
                    continue
                for i in range(len(wrong)):
                    self.add_ngrams(wrong[i], right[i])

        self.unigram_default_probability = 1 / self.unigram_number
        self.bigram_default_probability = 1 / self.bigram_number

        self.unigram_probabilities = dict(sorted(self.unigram_probabilities.items()))
        self.normalize('unigram')

        self.bigram_probabilities = dict(sorted(self.bigram_probabilities.items()))
        self.normalize('bigram')

    def normalize(self, stat_type):  # division by sum of fixes for wrong bigram
        prev_wrong = ''
        current_fixes = {}
        if stat_type == 'unigram':
            statistics = self.unigram_probabilities
        elif stat_type == 'bigram':
            statistics = self.bigram_probabilities
        else:
            return
        for wrong_bigram, right_bigram in statistics:
            if wrong_bigram != prev_wrong:
                s = sum(current_fixes.values())
                for w, r in current_fixes:
                    statistics[(w, r)] /= s
                prev_wrong = wrong_bigram
                current_fixes = {(wrong_bigram, right_bigram): statistics[(wrong_bigram, right_bigram)]}
            else:
                current_fixes[(wrong_bigram, right_bigram)] = statistics[(wrong_bigram, right_bigram)]
        s = sum(current_fixes.values())
        for w, r in current_fixes:
            statistics[(w, r)] /= s

    def add_ngrams(self, wrong, right):

        # add special characters for indicating the beginning and the end of the word
        # use double characters for separating bigrams
        wrong = ErrorModel.bigram_string(wrong)
        right = ErrorModel.bigram_string(right)
        # levenshtein matrix for two words of the query
        # first word is horizontal, second - vertical
        matrix = levenshtein_distance(right, wrong, result='matrix')

        # compute path in matrix for fixing the word
        # begin from lower right corner of the matrix
        # if next position is above current -> delete character (0)
        # if next position is from the left -> add character (1)
        # if the next position is diagonally -> replace character (2)
        x, y = len(wrong), len(right)
        while x != 0 or y != 0:
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
            self.bigram_probabilities[(wrong_bigram, right_bigram)] += 1
            self.bigram_number += 1

            self.unigram_probabilities[(wrong_bigram[0], right_bigram[0])] += 1
            self.unigram_number += 1

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

    # return probability of this fix
    def get_probability(self, wrong, right, unigram=False):

        if right == wrong:
            return 1

        if unigram:
            if (wrong, right) in self.unigram_probabilities:
                return self.unigram_probabilities[(wrong, right)]
            else:
                return self.unigram_default_probability
        else:
            if (wrong, right) in self.bigram_probabilities:
                return self.bigram_probabilities[(wrong, right)]
            else:
                return self.bigram_default_probability

    def get_weighted_distance(self, wrong, right):

        m, n = len(right), len(wrong)
        str1 = ErrorModel.bigram_string(right)
        str2 = ErrorModel.bigram_string(wrong)
        # now len(str1) = 2 * (m + 1), len(str2) = 2 * (n + 1)

        d = np.vstack((np.arange(m + 2)[np.newaxis],
                       np.hstack((np.arange(1, n + 2)[:, np.newaxis], np.zeros((n + 1, m + 1))))))

        for i in range(0, 2 * (m + 1), 2):
            for j in range(0, 2 * (n + 1), 2):
                weights = np.array([self.get_probability(str2[j:j + 2], '~' + str1[i + 1]),  # delete
                                    self.get_probability('~' + str2[j + 1], str1[i:i + 2]),  # add
                                    self.get_probability(str2[j:j + 2], str1[i:i + 2])])  # replace
                d[j // 2 + 1, i // 2 + 1] = np.min(np.array([d[j // 2, i // 2 + 1] + 1,  # delete
                                                             d[j // 2 + 1, i // 2] + 1,  # add
                                                             d[j // 2, i // 2] + int(str1[i] != str2[j])])  # replace
                                                   + (1 / weights))

        return d[n + 1, m + 1]

    @staticmethod
    def bigram_string(string, ngram=2):
        return "".join(list(map(lambda z: "".join(z), ngrams('^' + string + '_', ngram))))
