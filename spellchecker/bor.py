import re


class BorTree:

    def __init__(self, words):
        self.tree = TreeNode()
        self.read(words)
        self.em = None

    def read(self, words):
        for word in words:
            self.tree.insert(word)

    def search(self, word, max_lev):
        cur_row = range(len(word) + 1)
        res = []
        for letter in self.tree.children:
            self._search(self.tree.children[letter], letter, word, cur_row, res, max_lev)
        return res

    def _search(self, node, letter, word, prev_row, res, max_lev):
        columns = len(word) + 1
        cur_row = [prev_row[0] + 1]
        # compute levenshtein distance
        for column in range(1, columns):
            insert_cost = cur_row[column - 1] + 1
            delete_cost = prev_row[column] + 1
            replace_cost = prev_row[column - 1] + int(word[column - 1] != letter)
            cur_row.append(min(insert_cost, delete_cost, replace_cost))

        if cur_row[-1] <= max_lev and node.word:
            res.append([node.word, cur_row[-1]])

        if min(cur_row) <= max_lev:
            for letter in node.children:
                self._search(node.children[letter], letter, word, cur_row, res, max_lev)


class TreeNode:

    def __init__(self):
        self.word = None
        # {"letter" : TreeNode}
        self.children = {}

    def insert(self, word):
        node = self
        for letter in word:
            if letter not in node.children:
                node.children[letter] = TreeNode()
            node = node.children[letter]
        node.word = word
