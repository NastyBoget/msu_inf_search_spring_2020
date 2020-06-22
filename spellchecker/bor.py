# Fuzzy search in Bor realization

import pickle as pkl
from language_model import LanguageModel
from error_model import ErrorModel


class BorTree:

    def __init__(self):
        self.language_model = LanguageModel()
        self.error_model = ErrorModel()

        # [current_letter, {letter: line ...}, word_of_this_node]
        self.tree = [["", dict(), None]]
        self.tree_size = 0
        self.best_matches = {}
        self.error_threshold = 0
        self.str = ''

    def fit(self, language_model_f1):
        print('bor tree is fitting')
        self.language_model.load_unigram(language_model_f1)
        word_num = 0
        for word in self.language_model.unigram_probabilities:
            word_num += 1
            print(f"\r{word_num} lines are processed...", end='', flush=True)
            if not word:
                continue
            i, node = self.find_node(word)
            if i == -1 and node == -1:
                continue
            self.add_node(node, word[i])
            for char in word[i + 1:]:
                self.add_node(self.tree_size, char)
            self.tree[self.tree_size][2] = word

    def load_model(self, filename):
        with open(filename, "rb") as read_file:
            self.tree = pkl.load(read_file)

    def save_model(self, filename):
        with open(filename, "wb") as write_file:
            pkl.dump(self.tree, write_file, protocol=pkl.HIGHEST_PROTOCOL)

    # if the word is the prefix then it's inserted
    # if it's the new word, find the position for inserting
    def find_node(self, word, iteration=0, node=0):
        if len(word) <= iteration:
            self.tree[node][2] = word
            return -1, -1
        char = word[iteration]
        if char in self.tree[node][1]:
            return self.find_node(word, iteration + 1, self.tree[node][1][char])
        return iteration, node

    def add_node(self, node, char):
        self.tree_size += 1
        self.tree[node][1][char] = self.tree_size
        self.tree.append([char, dict(), None])

    def init_models(self, language_model_f1, error_model_f1, error_model_f2):
        self.language_model.load_unigram(language_model_f1)
        self.error_model.load_unigram(error_model_f1)
        self.error_model.load_bigram(error_model_f2)

    def find_best(self, string):
        self.best_matches = {string: 0}
        self.error_threshold = len(string) * 4
        self.str = string  # for get_best_word()
        self.get_best_word()
        for key in self.best_matches:
            self.best_matches[key] = (100000 * self.language_model.get_probability(key)) / \
                                     self.error_model.get_weighted_distance(string, key) ** 1 / 5
        # sort by score
        return sorted(self.best_matches.items(), key=lambda x: x[1], reverse=True)

    # dictionary of most fitted words
    def add_match(self, way, score):
        if way not in self.best_matches:
            self.best_matches[way] = score
            return
        self.best_matches[way] = min(self.best_matches[way], score)

    def get_best_word(self, error=0, pointer=-1, node=0, big_err=0):
        branches = self.tree[node][1]  # все возможные замены букв, идущие после этого префикса
        word = self.tree[node][2]  # слово этой вершины или none

        if error > self.error_threshold:
            return

        if word and (len(self.str) - 1 == pointer):
            self.add_match(word, error)
            return

        if len(self.str) - 1 <= pointer:
            return

        pointer += 1
        orig_char = self.str[pointer]
        for char, new_node in branches.items():
            self.get_best_word(
                error=error + self.get_error(orig_char, char),
                pointer=pointer,
                node=new_node,
                big_err=big_err)

            if big_err < 1:  # insertion or deletion of characters may occur once
                # insert
                self.get_best_word(
                    error=error + self.get_error('~', char),
                    pointer=pointer - 1,
                    node=new_node,
                    big_err=big_err + 1)

        if big_err < 1:  # insertion or deletion of characters may occur once
            if len(self.str) - 1 > pointer:
                orig_next_char = self.str[pointer + 1]
                next_node = branches.get(orig_next_char)
                if next_node:
                    # delete
                    self.get_best_word(
                        error=error + self.get_error(orig_char, '~'),
                        pointer=pointer + 1,
                        node=next_node,
                        big_err=big_err + 1)
            # delete last character in the word
            elif word:
                error += self.get_error(orig_char, '~')
                self.add_match(word, error)

    def get_error(self, wrong, right):
        if wrong == right:
            return 0
        return 1 / self.error_model.get_probability(wrong, right, unigram=True)
